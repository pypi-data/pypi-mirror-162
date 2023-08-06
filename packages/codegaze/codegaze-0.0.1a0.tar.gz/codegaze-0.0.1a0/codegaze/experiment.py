from dataclasses import asdict
import os
from typing import Any

import pandas as pd
from codegaze.datamodel import ExperimentConfig
from codegaze.utils import get_dirs, load_json, save_json
import numpy as np


class Experiment:
    """Experiment class to keep track of experiment configuration
    and data path. Each experiment is tied to data in a folder, beginning with the dataset, completion/metrics data is stored in subfolders.
    """

    def __init__(self, name: str, data_path: str = "experiments/data"):
        self.name = name
        self.config = None
        self.data_path = data_path

    def list_datasets(
        self,
    ) -> list[str]:
        """List all datasets for which experiments have been run."""
        return get_dirs(self.data_path)

    def list_dataset_problems(
        self, config: ExperimentConfig, model: str, metric_type: str = "function"
    ) -> list[str]:
        """List all problems for a dataset."""
        problem_path = os.path.join(
            self.data_path, config.dataset, config.slug, model, "metrics", metric_type
        )
        results = []
        if os.path.exists(problem_path):
            for problem in os.listdir(problem_path):
                problem_name = problem.split(".")[0]
                problem = load_json(os.path.join(problem_path, problem))
                results.append(
                    {
                        "name": problem_name,
                        "metrics": problem["metrics"],
                    }
                )
        return results

    def list_models(self, dataset: str, slug: str) -> list[str]:
        """List all models for a given experiment config."""
        model_path = os.path.join(self.data_path, dataset, slug)
        models = []
        if os.path.exists(model_path):
            models = get_dirs(model_path)
        return models

    def list_experiments(self, dataset: str) -> list[ExperimentConfig]:
        """List all experiments for a dataset."""
        exp_configs: list[ExperimentConfig] = []
        exp_path = os.path.join(self.data_path, dataset)
        if os.path.exists(exp_path):
            exps = get_dirs(exp_path)
            for exp in exps:
                exp_config_path = os.path.join(
                    self.data_path, dataset, exp, "config.json"
                )
                if os.path.exists(exp_config_path):
                    config = load_json(exp_config_path)
                    exp_configs.append(ExperimentConfig(**config))
        return exp_configs

    def load_metrics(
        self, config: ExperimentConfig, model: str, metric_type: str
    ) -> pd.DataFrame:
        metric_path = f"{self.data_path}/{config.dataset}/{config.slug}/{model}/metrics/{metric_type}"
        metrics = []
        metrics_arr = []
        if os.path.exists(metric_path):
            for file in os.listdir(metric_path):
                if file.endswith(".json"):
                    metric_file = os.path.join(metric_path, file)
                    if os.path.exists(metric_file):
                        metric_data = load_json(metric_file)
                        metrics.append(metric_data["metrics"])
                        metrics_arr.append(metric_data["metrics_arr"])
        return metrics, metrics_arr

    def get_aggregate_results(
        self, config: ExperimentConfig, model: str
    ) -> pd.DataFrame:
        """Get (mean) aggregated results for a given experiment config and model."""
        metric_types = ["function", "cat"]
        all = {}
        for metric_type in metric_types:
            metrics, _ = self.load_metrics(config, model, metric_type)
            metrics = pd.DataFrame(metrics).mean()
            all[metric_type] = metrics
        return all

    def agg_results(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """Aggregate experiments results."""
        agg_metric = pd.DataFrame((metrics.select_dtypes(include=np.number).mean())).T
        return agg_metric

    def get_rankings(self, model_results: Any):
        rankings = {}
        result = model_results[0]

        def sort_imp(result, target_metric):
            for metric_type in result["metrics"]:
                for metric in result["metrics"][metric_type].keys():
                    combined_metric = ":".join([metric_type, metric])
                    if combined_metric == target_metric:
                        return result["metrics"][metric_type][metric]

        def sortModels(results, targetMetric):
            results = sorted(
                results, key=lambda x: sort_imp(x, targetMetric), reverse=True
            )
            return results

        for metric_type in result["metrics"].keys():
            for metric in result["metrics"][metric_type].keys():
                combined_metric = ":".join([metric_type, metric])
                sorted_models = [
                    x["model"] for x in sortModels(model_results, combined_metric)
                ]
                sorted_models = ":".join(sorted_models)
                if sorted_models not in rankings:
                    rankings[sorted_models] = [combined_metric]
                else:
                    rankings[sorted_models] = rankings[sorted_models] + [
                        combined_metric
                    ]
        return rankings

    def get_problem_results(
        self,
        config: ExperimentConfig,
        model: str,
        problem: str,
        metric_type: str = "function",
    ) -> list[dict]:
        """Get results (completions, score metrics for each problem) for a given problem."""
        data_path = f"{self.data_path}/{config.dataset}/{config.slug}/{model}"
        completion_path = f"{data_path}/completions/{metric_type}/{problem}.json"

        metric_path = f"{data_path}/metrics/{metric_type}/{problem}.json"
        problem_results = {}
        if os.path.exists(completion_path):
            completion_data = load_json(completion_path)
            metric_data = load_json(metric_path)

            if metric_type == "function":
                holder = [
                    {
                        **{"metrics": cat},
                        **{"status": int(function[1]["passed"])},
                        **{"completion": completion},
                    }
                    for completion, function, cat in zip(
                        completion_data["bodies"],
                        metric_data["metrics_arr"]["function"]["0"],
                        metric_data["metrics_arr"]["cat"],
                    )
                ]
                problem_results = {
                    "completions": holder,
                    "solution": completion_data["solution"],
                    "prompt": completion_data["prompt"],
                    "test": completion_data["test"],
                }
            elif metric_type == "cat":
                # completions = completion_data["candidates"]
                # metrics = metric_data["results"]["0"]
                # result = [{"completion":c, "status": m[1]["passed"]} for c,m in  zip(completions, metrics)]
                return completion_data
        return problem_results

    def create_config(
        self,
        prompt_tokens: int = 1,
        n_completions: int = 100,
        lines_per_block: int = 10,
        temperature: float = 0.5,
        parser_retry: bool = True,
        suffix: bool = False,
    ) -> ExperimentConfig:
        slug: str = str(
            f"pt{prompt_tokens}_ml{lines_per_block}_t{temperature}_suff{str(int(suffix))}"
        )
        config = {
            "prompt_tokens": prompt_tokens,
            "n_completions": n_completions,
            "lines_per_block": lines_per_block,
            "temperature": temperature,
            "slug": slug,
            "parser_retry": parser_retry,
            "suffix": suffix,
        }
        config = ExperimentConfig(**config)
        self.config = config
        return config

    def save_config(self, config: ExperimentConfig, path: str) -> None:
        """Save experiment config to file."""
        save_json(asdict(config), path)
