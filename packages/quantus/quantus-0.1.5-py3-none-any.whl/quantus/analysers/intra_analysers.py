from typing import Dict, Union, List
import random
from sklearn.model_selection import ParameterGrid
from quantus.helpers.model_interface import ModelInterface


class ParameterSensitivityAnalysis(Analyser):
    """
    Analyser to investigate the impact of that each feature has on the evaluation outcome.
    Assessing how sensitive the metric is to different parameterisations.

    Approaches:
     1. measure the effect that one parameter while fixing other variables (if n = 1)
     2. do step 1. n times while randomly selecting from the parameterisation_grid

    If n = 1, the first value in each setting is picked.
    default_value: Union[str, None] = "random",

    """

    def __init__(
        self,
        metric: quantus.Metric,
        params: Dict[str, np.array],
        search_type: str = "grid_search",
        nr_runs: int = 1,
        max_iters: int = 10000,
    ):

        assert search_type in [
            "grid_search",
            "random_search",
        ], "Acceptable input for 'search_type' is 'grid_search' or 'random_search'"
        self.metric = metric
        self.params = params
        self.search_type = search_type
        self.nr_runs = nr_runs
        self.max_iters = max_iters
        self.grid = self.get_grid
        self.total_combinations = len(self.get_grid)
        self.results = {}

    def __call__(
        self,
        model: quantus.ModelInterface,
        x_batch: np.array,
        y_batch: np.array,
        a_batch: Union[np.array, None],
        s_batch: Union[np.array, None],
        *args,
        **kwargs,
    ):

        # Get explanation func to evaluate with.
        explain = kwargs["explain_func"]
        a_batch = explain(model=model, inputs=x_batch, targets=y_batch, **kwargs)

        # Loop over the possible parameter space and nr_runs and store evaluation outcome.

        # TODO. Implement random search.
        self.results = {}
        for i, p in enumerate(self.grid):
            sub_results = []
            for iter in range(self.nr_runs):
                scores = metric(**{**p, **{"disable_warnings": True}})(
                    model=model,
                    x_batch=x_batch,
                    y_batch=y_batch,
                    a_batch=a_batch,
                    s_batch=s_batch,
                    *args,
                    **kwargs,
                )
                sub_results.append(scores)

            self.results[i] = np.array(sub_results).flatten()

        return self.results

    @property
    def get_grid(self) -> List[dict]:
        try:
            if self.grid:
                return self.grid
        except:
            params = list(ParameterGrid(self.params))
            if len(params) > self.max_iters:
                return random.choice(params, size=self.max_iters)
            else:
                return params

    @property
    def _get_results(self):
        assert (
            self.results
        ), "Call the ParameterSensitivityAnalysis instance before calling .get_results."
        return self.results

    @property
    def _get_results_dict(self):
        assert (
            self.results
        ), "Call the ParameterSensitivityAnalysis instance before plotting."
        grid_indices = {}
        for k, v in self.params.items():
            for i in v:
                self.results[f"{k}={i}"] = []
                for index, g in enumerate(self.grid):
                    if g.get(k) == i:
                        grid_indices[f"{k}={i}"].append(index)
        return grid_indices

    @property
    def _get_results_df(self):
        data = {}
        row = 0
        for (index, r), p in zip(self.results.items(), self.grid):
            for k, v in p.items():
                for i in r:
                    data[row] = {"Index": index, "Score": i, "Parameter": k, "Value": v}
                    row += 1
        df = pd.DataFrame(data).T

        # Remove variable from list if there is only one unique value,
        for k in df.Parameter.unique():
            if df.loc[(df.Parameter == k), "Value"].nunique() == 1:
                df.drop(df.loc[(df.Parameter == k), "Value"].index, inplace=True)

        return df

    def plot_scores_by_parameter(
        self, kind: str = "bar", path_to_save: Union[None, str] = None, *args, **kwargs
    ):

        sns.catplot(
            x="Score",
            y="Parameter",
            hue="Value",
            kind="swarm",
            data=self._get_results_df,
            *args,
            **kwargs,
        )
        plt.show()

        if path_to_save:
            plt.savefig(path_to_save, dpi=400)

    @property
    def get_sensitivity():
        pass

    def plot(self):
        assert (
            self.results
        ), "Call the ParameterSensitivityAnalysis instance before plotting."

        # plt.xlabel(params.keys())
        # sns.catplot(x="Scores", y="Parameter", hue="Value", kind="swarm", data=tips)



class RandomisationAnalysis(Analyser):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def make_random_model(self) -> ModelInterface:
        pass

    def make_random_explanations(self) -> np.array:

        # What make sense as a baseline?

        # Random blob, localised.

        # Random noise.

        # ...
        pass

    def compute_metric_decay(self):
        """Interpret"""
        pass

    def plot_randomsiation_results(self):
        pass


    def analyse_p_value(self,

        scores_attribution: List[int, float, bool],
        scores_random: List[int, float, bool],
        thresold: float = 0.05,
    ):
        """Returns p-value wilcoxon_signed_rank_test to see that"""
        return scipy.stats.wilcoxon(scores_attribution, scores_random)[1]



'''
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Union
from itertools import product

def score_variability_analysis(scores_attribution: List[int, float, bool]):
    """Std between different samples."""
    pass


def label_randomisation_analysis(metric: Metric):
    """If we are randomising the classes to explain... asking for metrics to degrade."""
    pass


def weight_randomisation_analysis(metric: Metric):
    """If we are randomising the classes to explain... asking for metrics to degrade."""
    pass


def explanation_artefact_analysis(metric: Metric):
    """If we are creating an artefact in explanation... asking for metrics to degrade."""
    pass

'''
