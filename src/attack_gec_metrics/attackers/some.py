from .base import AttackerBase
from dataclasses import dataclass, field
from gec_datasets import GECDatasets
from gec_metrics import get_metric
import math
import numpy as np
from pathlib import Path
import torch
from tqdm import tqdm
import json
import pprint
from tqdm import tqdm

class AttackerForSOME(AttackerBase):
    @dataclass
    class Config(AttackerBase.Config):
        data_ids: list[str] = field(
            default_factory=lambda: [
                'lang8-train',
                'fce-train', 'wi-locness-train', 'nucle-train',
                # 'troy-1bw-train', 'troy-blogs-train'
            ]
        )
        index_dir: str = 'exp-datasets/index'
        k: int = 256

    def __init__(self, config=None) -> None:
        super().__init__(config)
        Path(self.config.index_dir).mkdir(exist_ok=True, parents=True)
        some_cls = get_metric('some')
        self.some = some_cls(some_cls.Config(
            weight_g=0.55,
            weight_f=0.43,
            weight_m=0,
            batch_size=128
        ))
        gec = GECDatasets('exp-datasets')
        self.srcs = []
        self.text = []
        self.config.data_ids = sorted(self.config.data_ids)
        for data_id in self.config.data_ids:
            self.srcs += gec.load(data_id).srcs
            self.text += gec.load(data_id).refs[0]
        
    def correct(self, sources: list[str]) -> list[str]:
        scores = self.some.score_sentence(self.srcs, self.text)
        best_hyp = self.text[scores.index(max(scores))]
        return [best_hyp] * len(sources)