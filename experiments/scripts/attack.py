from dataclasses import dataclass, field
from gec_datasets import GECDatasets
from attack_gec_metrics import get_attacker, get_attacker_ids
import argparse
from pathlib import Path

def main(args):
    gec = GECDatasets('exp-datasets')
    att_cls = get_attacker(args.att_id)
    config_args = dict()
    if args.att_id in ['some', 'impara']:
        corpus = []
        for i in args.corpus_ids:
            corpus += gec.load(i).refs[0]
        config_args['corpus'] = corpus
    if args.att_id == 'impara':
        # determine the directory name of an index like "fce-train[SEP]lang8-train"
        concat_ids = '[SEP]'.join(args.corpus_ids)
        config_args['index_dir'] = f'exp-datasets/index/{concat_ids}'
    attcker = att_cls(att_cls.Config(**config_args))
    srcs = gec.load(args.data).srcs[:100]
    hyps = attcker.correct(srcs)
    Path(args.out).write_text('\n'.join(hyps))

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--att_id', choices=get_attacker_ids())
    parser.add_argument('--data', default='bea19-dev')
    parser.add_argument('--corpus_ids', nargs='+', default=['fce-train', 'lang8-train', 'wi-locness-train', 'nucle-train'])
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)