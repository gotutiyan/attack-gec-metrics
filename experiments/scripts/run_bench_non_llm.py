from attack_gec_metrics import get_bench, get_bench_ids
from gec_metrics.metrics import SOME, Scribendi, IMPARA
import argparse

def main(args):
    metrics = [SOME(), Scribendi(), IMPARA()]
    bench_cls = get_bench(args.bench)
    benchmark = bench_cls('exp-outputs')
    benchmark.run(metrics=metrics)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bench', choices=get_bench_ids(), default='pillars')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)