from benchmark import get_bench
from gec_metrics.metrics import SOME, Scribendi, IMPARA, LLMKobayashi24HFSent
import argparse

def table():
    benchmark = get_bench('pillars')('exp-outputs')
    names = [
        'SOME.json',
        'Scribendi.json',
        'IMPARA.json',
        'LLMKobayashi24OpenAISent/gpt-4o-mini-2024-07-18.json',
        'LLMKobayashi24HFSent/google/gemma-3-27b-it.json',
        'LLMKobayashi24HFSent/meta-llama/Llama-3.3-70B-Instruct.json',
        'LLMKobayashi24OpenAIEdit/gpt-4o-mini-2024-07-18.json',
        'LLMKobayashi24HFEdit/google/gemma-3-27b-it.json',
        'LLMKobayashi24HFEdit/meta-llama/Llama-3.3-70B-Instruct.json'
    ]
    scores = {name: benchmark.load_json(name) for name in names}
    latex_table = benchmark.latexfy(scores, benchmark.load_name())
    print(latex_table)

def ensemble():
    benchmark = get_bench('pillars')('exp-outputs')
    names = [
        'SOME.json',
        'Scribendi.json',
        'IMPARA.json',
        'LLMKobayashi24OpenAISent/gpt-4o-mini-2024-07-18.json',
        'LLMKobayashi24HFSent/google/gemma-3-27b-it.json',
        'LLMKobayashi24HFSent/meta-llama/Llama-3.3-70B-Instruct.json',
        'LLMKobayashi24OpenAIEdit/gpt-4o-mini-2024-07-18.json',
        'LLMKobayashi24HFEdit/google/gemma-3-27b-it.json',
        'LLMKobayashi24HFEdit/meta-llama/Llama-3.3-70B-Instruct.json'
    ]
    scores = {name: benchmark.load_json(name) for name in names}
    ens_scores = benchmark.ensemble(scores)
    latex_table = benchmark.latexfy(ens_scores, benchmark.load_name())
    print(latex_table)
    

def table_t():
    benchmark = get_bench('pillars')('exp-outputs')
    scores = {
        name: benchmark.load_json(f'LLMKobayashi24HFEdit/{name}.json')
        for name in [
            'Qwen/Qwen2.5-1.5B-Instruct',
            'Qwen/Qwen2.5-3B-Instruct',
            'Qwen/Qwen2.5-7B-Instruct',
            'Qwen/Qwen2.5-14B-Instruct',
            'Qwen/Qwen2.5-32B-Instruct',
            'Qwen/Qwen3-1.7B',
            'Qwen/Qwen3-8B',
            'Qwen/Qwen3-32B',
            'google/gemma-2-2b-it',
            'google/gemma-2-9b-it',
            'google/gemma-2-27b-it',
            'google/gemma-3-1b-it',
            'google/gemma-3-4b-it',
            'google/gemma-3-12b-it',
            'google/gemma-3-27b-it',
            'meta-llama/Llama-2-7b-chat-hf',
            'meta-llama/Llama-2-13b-chat-hf',
            'meta-llama/Llama-2-70b-chat-hf',
            'meta-llama/Meta-Llama-3-8B-Instruct',
            'meta-llama/Meta-Llama-3-70B-Instruct',
            'meta-llama/Llama-3.3-70B-Instruct',
            'microsoft/Phi-4',
            '01-ai/Yi-1.5-6B-Chat',
            '01-ai/Yi-1.5-9B-Chat',
            '01-ai/Yi-1.5-34B-Chat',
        ]
    }
    print(benchmark.latexfy_transpose(scores, benchmark.load_name()))

def main(args):
    ensemble()
    # table()
    # table_t()
    

def get_parser():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)