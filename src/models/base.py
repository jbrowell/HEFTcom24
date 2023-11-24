from abc import abstractmethod

from pandas import DataFrame


class BaseForecaster:
    def __init__(self, config):
        super(BaseForecaster, self).__init__()
        self.config = config

    @abstractmethod
    def fit(self, *inputs: DataFrame) -> DataFrame:
        # Quantiles in cofig
        pass

    @abstractmethod
    def predict(self, *inputs: DataFrame) -> DataFrame:
        pass
