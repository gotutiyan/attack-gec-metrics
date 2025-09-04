from gec_metrics.metrics import Scribendi
from transformers import pipeline
from .base import AttackerBase
from  dataclasses import dataclass
import torch
from tqdm import tqdm
import spacy

class AttackerForScribendi(AttackerBase):
    @dataclass
    class Config(AttackerBase.Config):
        mask_model: str = "google-bert/bert-base-cased"
        top_k: int = 64

    def __init__(self, config=None) -> None:
        super().__init__(config)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.unmasker = pipeline(
            'fill-mask',
            model=self.config.mask_model,
            device=device,
            top_k=self.config.top_k
        )
        self.scribendi = Scribendi()
        self.nlp = spacy.load('en_core_web_sm')

    def tokenize(self, sent):
        doc = self.nlp(sent)
        return ' '.join([tok.text for tok in doc])

    def correct(self, sources: list[str]):
        hyps = []
        src_ppls = self.scribendi.ppl(sources)
        for sent_id, src in tqdm(enumerate(sources), total=len(sources), disable=not self.config.show_tqdm):
            tokens = src.split(' ')
            best_hyp = src
            found = False
            for token_id in range(len(tokens)):
                masked_tokens = tokens[:]
                masked_tokens[token_id] = self.unmasker.tokenizer.mask_token
                masked_sent = ' '.join(masked_tokens)
                fill_results = self.unmasker(masked_sent)
                hyp_cands = [
                    self.tokenize(elem['sequence']) for elem in fill_results
                ]
                hyp_ppls = self.scribendi.ppl(hyp_cands)
                is_win = [src_ppls[sent_id] > h for h in hyp_ppls]
                for i, w in enumerate(is_win):
                    if not w:  # ignore lose samples
                        continue
                    if tokens[token_id] == fill_results[i]['token_str']:
                        # Ignore if same as source
                        continue
                    best_hyp = hyp_cands[i]
                    found = True
                    if self.config.verbose:
                        print(f'{sent_id=}', f'{token_id=}', f"{src_ppls[sent_id]:.4f} {hyp_ppls[i]} {tokens[token_id]} -> {fill_results[i]['token_str']}")
                    break
                if found:
                    break
            if self.config.verbose:
                print(f"{src}\n{best_hyp}\n\n")
            hyps.append(best_hyp)
        assert len(hyps) == len(sources)
        scores = self.scribendi.score_sentence(sources, hyps)
        for i in range(len(scores)):
            if scores[i] == -1:
                # -1 means surface agreement filtered the hypotheses.
                # In this case, it uses the source as the hypothesis to minimize the penalty.
                hyps[i] = sources[i]
        return hyps