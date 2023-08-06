from typing import Dict


def rank_consistency_analysis(evaluation_results: dict, plot=True):
    """..."""
    for metric, scores in evaluation_results.items():
        pass
    return None


def time_efficiency_analysis(
    metrics: Dict[str:Metric],
    model: ModelInterface,
    x_batch: np.array,
    y_batch: np.array,
    a_batch: Union[np.array, None],
    s_batch: Union[np.array, None],
    *args,
    **kwargs,
):
    pass


def uniquness_analysis(explanations: Dic[str, np.array]):
    """If explanations are all the same in the classes = 1.0, it is unverifiable."""
    pass


from typing import Dict, Union, List
import random
from sklearn.model_selection import ParameterGrid


class RandomisationAnalysis:
    pass


class ParameterSensitivityAnalysis:
    def __init__(
        self,
        metric: quantus.Metric,
        params: Dict[str, np.array],
        nr_runs: int = 10,
        max_iters: int = 10000,
    ):

        self.metric = metric
        self.params = params
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

        # Get the possible parameter space.
        params = self.get_grid

        # Get explanation func to evaluate with.
        explain = kwargs["explain_func"]
        a_batch = explain(model=model, inputs=x_batch, targets=y_batch, **kwargs)

        self.results = {}
        for i, p in enumerate(params):
            self.results[i] = metric(**{**p, **{"disable_warnings": True}})(
                model=model,
                x_batch=x_batch,
                y_batch=y_batch,
                a_batch=a_batch,
                s_batch=s_batch,
                *args,
                **kwargs,
            )
        return self.results

    @property
    def get_grid(self) -> List[dict]:
        try:
            if self.grid:
                return self.grid
        except:
            params = list(ParameterGrid(self.params))
            if len(params) > self.max_iters:
                return random.choice(params, size=self.max_parameterisations)
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

    def plot_score_distribution_by_parameter(self):
        sns.catplot(
            x="Score",
            y="Parameter",
            hue="Value",
            kind="swarm",
            data=self._get_results_df,
        )
        plt.show()

    def plot_sensitivity_by_parameter(self):
        pass

    @property
    def get_sensitivity():
        pass

    def plot(self):
        assert (
            self.results
        ), "Call the ParameterSensitivityAnalysis instance before plotting."

        # plt.xlabel(params.keys())
        # sns.catplot(x="Scores", y="Parameter", hue="Value", kind="swarm", data=tips)