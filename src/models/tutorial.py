import statsmodels.formula.api as smf
from pandas import DataFrame

from loaders import register
from models import BaseForecaster


class QuantRegModel(BaseForecaster):
    def __init__(self, config, inputs) -> None:
        super(QuantRegModel, self).__init__(config, inputs)
        self.model = smf.quantreg(
            formula=self.config.formula,
            data=inputs,
        )
        self.max_iter = self.config.max_iter

    def fit(self, quantile) -> DataFrame:
        return self.model.fit(
            q=quantile / 100,
            max_iter=self.max_iter,
        )

    def predict(self, data: DataFrame) -> DataFrame:
        return self.model.predict(data)


def initialize():
    register("model", QuantRegModel)
