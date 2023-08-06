# CodeGaze [Beta]: A library for evaluating and debugging code generation models

> Still in development.

Code gaze implements a set of evaluation metrics and visualization tools for debugging code generation models.

![](docs/images/screen.jpg)

CodeGaze is build around a set of abstractions that allow for the evaluation of code generation models.

- Dataset: An example code generation dataset e.g. humaneval.
- Experiment: A set of parameters that define the evaluation of a code generation model. Each experiment specifies things like the dataset, model properties (temperature, n_completions), and some metric properties.
- Model: A code generation model that can be evaluated. This is either an OpenAI model or a HuggingFace model.

The basic starting point is to run an experiment on a dataset with a list of models.

## Installation

```bash
pip install codegaze
```
