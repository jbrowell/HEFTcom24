"Testing Model Configurations based on `Getting Started` notebook"
import os

import statsmodels.formula.api as smf
from dotenv import load_dotenv
from omegaconf import OmegaConf

from config import QuantRegConfig
from loaders import get_local_data, load_module

if __name__ == "__main__":
    load_dotenv()
    root = os.getenv("root")
    data_dir = os.path.join(root, "data/")

    inputs = get_local_data(data_dir)

    config = QuantRegConfig()
    model = load_module("model", config, inputs)
    forecast_models = dict()

    for q in range(10, 100, 10):
        print(f"Starting Predictions for q{q}")

        forecast_models[f"q{q}"] = model.fit(quantile=q / 100)
        inputs[f"q{q}"] = forecast_models[f"q{q}"].predict(inputs)
        inputs.loc[inputs[f"q{q}"] < 0, f"q{q}"] = 0

    print(forecast_models)
