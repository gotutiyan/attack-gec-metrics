from dataclasses import dataclass, field
from gec_datasets import GECDatasets
from attack_gec_metrics import get_attacker, get_attacker_ids
import argparse
from pathlib import Path

def main(args):
    gec = GECDatasets('exp-datasets').load(args.data)
    att_cls = get_attacker(args.att_id)
    attcker = att_cls(att_cls.Config())
    hyps = attcker.correct(gec.srcs)
    Path(args.out).write_text('\n'.join(hyps))

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--att_id', choices=get_attacker_ids())
    parser.add_argument('--data', default='bea19-dev')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)