from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Config:
    meta: Any
    data_params: Any
    model_params: Any
    trainer_params: Any


#  ╭──────────────────────────────────────────────────────────╮
#  │ Model Configurations                                     │
#  ╰──────────────────────────────────────────────────────────╯


@dataclass
class ModelConfig:
    name: str
    config: Any


@dataclass
class ForecasterConfig:
    module: str = "models.base"
    quantile: int = 0.1
    # TODO: Other set configurations shared for forecasters?


@dataclass
class QuantRegConfig:
    module: str = "models.tutorial"
    formula: str = (
        "total_generation_MWh ~ bs(SolarDownwardRadiation,df=5) + bs(WindSpeed,df=8)"
    )
    quantile: int = 0.1
    max_iter: int = 2500
