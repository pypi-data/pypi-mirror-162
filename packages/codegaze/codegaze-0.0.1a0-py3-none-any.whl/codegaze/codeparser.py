
from codegaze.datamodel import CodeBlock
from tree_sitter import Language, Node, Parser, Tree
import os
import codegaze as cg


class TreeSitterParser():
    """A parser for TreeSitter."""

    def __init__(self, language: str = "python"):
        # TODO: create mechanish to update supported languages
        self.supported_languages = ["python", "javascript"]
        self.parser: Parser = Parser()
        self.build_languages()
        self.set_language(language)

    def get_grammars(self):
        cwd = os.getcwd()
        os.makedirs(self.tree_sitter_path, exist_ok=True)
        os.chdir(self.tree_sitter_path)

        for language in self.supported_languages:
            if not os.path.exists(os.path.join(self.tree_sitter_path, "tree-sitter-" + language)):
                os.system(f"git clone https://github.com/tree-sitter/tree-sitter-{language}")
        os.chdir(cwd)

    def list_languages(self):
        return self.supported_languages

    def build_languages(self):
        module_path = os.path.dirname(os.path.abspath(cg.__file__))
        self.tree_sitter_path = os.path.join(module_path, 'treesitter-languages')
        self.language_build_path = os.path.join(self.tree_sitter_path, "build", "my-languages.so")
        if not os.path.exists(self.language_build_path):
            self.get_grammars()
            Language.build_library(
                self.language_build_path,
                [os.path.join(self.tree_sitter_path, "tree-sitter-" + language)
                 for language in self.supported_languages])

    def set_language(self, language_name: str = "python"):
        LANGUAGE = Language(self.language_build_path, 'python')
        if language_name == "javascript":
            LANGUAGE = Language(self.language_build_path, 'javascript')
        self.parser.set_language(LANGUAGE)


class CodeBlockParser():
    """Parse a code string and return a serialized list of CodeBlock objects
    """

    def __init__(self, parser: Parser = TreeSitterParser()):
        if isinstance(parser, TreeSitterParser):
            self.parser = parser.parser
        elif isinstance(parser, Parser):
            self.parser = parser
        else:
            raise TypeError("parser must be of type TreeSitterParser or Parser")

    def parse_string(self, code_string: str, error_retry: bool = False) -> Node:
        """Return root node of tree for given code string

        Args:
            code_string (str): str representing code
            error_retry (bool, optional): remove last line of codestring and
                retry parsing if root node is error. Defaults to False.

        Returns:
            _type_: _description_
        """
        code_byte: bytes = bytes(code_string, "utf8")
        tree: Tree = self.parser.parse(code_byte)
        cursor = tree.walk()   # type: ignore
        root = cursor.node
        if error_retry:
            error_count = 0
            while (root.type == "ERROR" and root):
                error_count += 1
                # remove last line from code_string and call again
                code_string = code_string[:code_string.rfind('\n')]
                code_byte = bytes(code_string, "utf8")
                tree = self.parser.parse(code_byte)
                cursor = tree.walk()   # type: ignore
                root = cursor.node
        return root

    def walk(self, code_string: str, named_only: bool = False,
             error_retry: bool = False) -> list[CodeBlock]:
        """Return array of blocks for given code bytes

        Args:
            code_string (str): string representing code
            named_only (bool, optional): retry parsing if root node is error. Defaults to False.

        Returns:
            list[dict]: list of discovered blocks
        """
        # convert code string to tree, traverse tree bfs
        code_bytes = bytes(code_string, "utf8")
        root: Node = self.parse_string(code_string, error_retry=error_retry)
        queue: list[tuple[Node, int, int]] = [(root, 0, 0)]
        blocks: list[CodeBlock] = []  # list representation of code string
        token_index = 0
        while queue:
            node, h, parent_index = queue.pop()
            if node:
                if named_only and not node.is_named:
                    continue
                if node.type != "module":
                    block_text = code_bytes[node.start_byte: node.end_byte].decode("utf-8")
                    token_index += 1
                    block = CodeBlock(
                        type=node.type,
                        text=block_text,
                        h=h,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        num_lines=len(block_text.split("\n")),
                        is_named=node.is_named,
                        child_count=node.child_count,
                        parent_index=parent_index
                    )
                    blocks.append(block)
                if node.children:
                    h = h + 1
                    for child in node.children[::-1]:
                        queue.append((child, h, token_index))  # type: ignore
        return blocks

    def extract_blocks(
            self,
            code_string: str,
            max_lines_per_block: int = 10,
            skip_parent_block: bool = True,
            error_retry: bool = False,
            named_only: bool = True) -> list[CodeBlock]:
        """Extract blocks from code string and return list of CodeBlock objects
            Args:
                code_string (str): string representing code
                max_lines_per_block (int, optional): max number of lines per block. Defaults to 10.
                skip_parent_block (bool, optional): skip parent block. Defaults to True.
                named_only (bool, optional): skip unnamed blocks. Defaults to True.
            Returns:
                list[CodeBlock]: list of discovered blocks
        """

        extracted_blocks: list[CodeBlock] = []
        all_blocks: list[CodeBlock] = self.walk(
            code_string, named_only=named_only, error_retry=error_retry)
        block_index: int = 0

        def process_block(block: CodeBlock, block_index: int) -> int:
            block.block_index = block_index
            extracted_blocks.append(block)
            return block_index + 1

        current_depth = 1
        last_expand_point = 1
        for block in all_blocks:
            if block.type == "block" and block.num_lines >= max_lines_per_block:
                last_expand_point = block.h
                current_depth = block.h + 1
                if skip_parent_block:
                    extracted_blocks.pop()
            elif block.h == current_depth and block.is_named:
                block_index = process_block(block, block_index)
            elif block.h < last_expand_point:
                current_depth = block.h
                last_expand_point = block.h
                block_index = process_block(block, block_index)
        return extracted_blocks
