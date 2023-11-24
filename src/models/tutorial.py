import statsmodels.formula.api as smf
from base import BaseForecaster
from pandas import DataFrame


class QuantRegModel(BaseForecaster):
    def __init__(
        self,
        quantile,
        max_iter,
    ) -> None:
        super(BaseForecaster, self).__init__(config)
        self.quantile = quantile / 100
        self.max_iter = max_iter

    def fit(self, formula, inputs: DataFrame) -> DataFrame:
        self.input = inputs
        self.model = smf.quantreg(
            formula=formula,
            data=inputs,
        )
        return self.model.fit(
            q=self.quantile,
            max_iter=self.max_iter,
        )

    def predict(self) -> DataFrame:
        return self.model.predict(self.input)
