from dataclasses import dataclass, asdict
from gec_metrics.metrics import LLMKobayashi24HFSent, LLMKobayashi24OpenAISent, LLMKobayashi24HFEdit, LLMKobayashi24OpenAIEdit
from benchmark import get_bench, get_bench_ids
import itertools
import json
import pprint
from pathlib import Path
import torch

class ExpLLM:
    @dataclass
    class Config:
        benchmark: str = None
        metric_type: str = 'hf-sent'
        model: str = 'meta-llama/Llama-2-13b-chat-hf'

    def __init__(self, config=None):
        self.config = config if config is not None else self.Config()
        cache_path = Path('exp-outputs/cache/') / (self.config.model.replace('/', '-') + '.cache')
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        llm_config = {
            'model': self.config.model,
            'cache': cache_path,
            'dtype': 'float32',
            'quantization': '4bit' if '70b' in self.config.model.lower() else '8bit'
        }
        llm_cls = {
            'hf-sent': LLMKobayashi24HFSent,
            'hf-edit': LLMKobayashi24HFEdit,
            'openai-sent': LLMKobayashi24OpenAISent,
            'openai-edit': LLMKobayashi24OpenAIEdit,
        }[self.config.metric_type]
        self.llm = llm_cls(llm_cls.Config(**llm_config))
        self.benchmark = self.config.benchmark('exp-outputs')
        self.hyps = self.benchmark.load_hyps()
        self.srcs = self.benchmark.srcs

    @torch.inference_mode()
    def run_bench(self):
        self.benchmark.subsetalize()
        scores = self.benchmark.run(
            metrics=[self.llm],
        )
        # E.g., 'exp-outputs/BenchmarkPillars/LLMKobayashi24OpenAISent/Qwen/Qwen2.5-14B-Instruct.json'
        self.benchmark.save_json(scores, f'{self.llm.__class__.__name__}/{self.llm.config.model}.json')

import argparse

def main(args):
    bench_cls = get_bench(args.bench)
    exp = ExpLLM(ExpLLM.Config(
        benchmark=bench_cls,
        metric_type=args.metric_type,
        model=args.model
    ))
    exp.run_bench()

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--metric_type', default='hf-sent')
    parser.add_argument('--model', default='Qwen/Qwen2.5-14B-Instruct')
    parser.add_argument('--bench', choices=get_bench_ids(), default='pillars')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)
