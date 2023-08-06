from datasets import load_dataset


class CodeGazeDataset:
    """
    Base class for all datasets.
    """
    def __init__(self, name: str = "humaneval"):
        self.name = name


class HumanEvalDataset(CodeGazeDataset):
    """
    HumanEval dataset.
    """

    def __init__(self, name: str = "humaneval"):
        super().__init__(name)
        self.problems = load_dataset("openai_humaneval")["test"]

    def list_problems(self) -> list[str]:
        return [x["task_id"].replace("/", "") for x in self.problems]


class P3Dataset(CodeGazeDataset):
    """
    P3 dataset.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def load_data(self) -> list[str]:
        raise NotImplementedError()

 