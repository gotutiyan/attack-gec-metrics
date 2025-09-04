from .base import AttackerBase
from dataclasses import dataclass
from gec_metrics import get_metric

class AttackerForSOME(AttackerBase):
    @dataclass
    class Config(AttackerBase.Config):
        # data_ids: list[str] = field(
        #     default_factory=lambda: [
        #         'lang8-train',
        #         'fce-train', 'wi-locness-train', 'nucle-train',
        #         # 'troy-1bw-train', 'troy-blogs-train'
        #     ]
        # )
        corpus: list[str] = None
        weight_g: float = 0.55
        weight_f: float = 0.43

    def __init__(self, config=None) -> None:
        super().__init__(config)
        some_cls = get_metric('some')
        self.some = some_cls(some_cls.Config(
            weight_g=self.config.weight_g,
            weight_f=self.config.weight_f,
            weight_m=0.0,  # ignore meaning score
            batch_size=self.config.batch_size
        ))
        # We ignore the meaning score, so srcs will not be used.
        self.scores = self.some.score_sentence(
            self.config.corpus,  # Just for interface, this will not be used.
            self.config.corpus
        )
        self.best_hyp = self.config.corpus[self.scores.index(max(self.scores))]
        
    def correct(self, sources: list[str]) -> list[str]:
        # return the best sentence for all of inputs
        return [self.best_hyp for _ in sources]