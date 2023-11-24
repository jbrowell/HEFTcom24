from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Config:
    meta: Any
    data_params: Any
    model_params: Any
    trainer_params: Any


@dataclass
class ModelConfig:
    name: str
    config: Any
