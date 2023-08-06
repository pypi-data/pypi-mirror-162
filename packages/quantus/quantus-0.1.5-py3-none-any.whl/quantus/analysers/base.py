import numpy as np
import Union


class Analyser:

    def __init__(self, *args, **kwargs):
        pass

    def __call__(
        self,
        model,
        x_batch: np.ndarray,
        y_batch: Union[np.ndarray, int],
        a_batch: Union[np.ndarray, None],
        s_batch: Union[np.ndarray, None],
        *args,
        **kwargs,
    ) -> Union[int, float, list, dict, None]:
        raise NotImplementedError
