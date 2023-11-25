from abc import abstractmethod

from pandas import DataFrame


class BaseForecaster:
    def __init__(self, config, inputs: DataFrame):
        self.config = config
        self.inputs = inputs

    @abstractmethod
    def fit(self, quantile) -> DataFrame:
        pass

    @abstractmethod
    def predict(self, data: DataFrame) -> DataFrame:
        pass
