# from dataclasses import dataclass
from pydantic.dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Number of tokens to be added to the block for CAT metrics"""

    prompt_tokens: int  # number of added tokens to blocks
    n_completions: int  # number
    lines_per_block: int
    slug: str = ""
    model_type: str = "openai"
    model_suffix: bool = False
    dataset: str = "humaneval"
    parser_retry: bool = True
    temperature: float = 0.2
    suffix: bool = False


@dataclass
class CodeBlock:
    """A code block extracted from a Code fragment or Function."""

    type: str
    """The type of the code block. This correspondes to a tree-sitter node type name."""

    text: str
    """The text of the code block."""

    h: int
    """The height index of the block in the fragment AST tree."""

    start_byte: int
    """The byte offset of the start of the code block in the fragment AST tree."""

    end_byte: int
    """The byte offset of the end of the code block in the fragment AST tree."""

    num_lines: int
    """The number of lines in the code block."""

    is_named: bool
    """Whether the code block is a named treesitter node."""

    child_count: int
    """The number of children of the code block."""

    parent_index: int
    """The index of the parent of the code block in the array serialized fragment AST tree."""

    block_index: int = 0
    """The index of the extracted block in function."""
