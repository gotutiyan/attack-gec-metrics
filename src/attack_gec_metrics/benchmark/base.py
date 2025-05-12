from dataclasses import dataclass
import abc
from gec_metrics.metrics import MetricBase
from gec_datasets import GECDatasets
import json
from pathlib import Path

class BenchmarkBase(abc.ABC):
    # @dataclass
    # class Config:
    #     base_path: str = 'exp-datasets'
    def __init__(self, base_path: str = 'exp-outputs'):
        self.base_path = Path(base_path) / self.__class__.__name__
        self.gec = GECDatasets('exp-datasets')
        
    def run(
        self,
        metrics: list[MetricBase]
    ):
        '''Run evaluation using specified metrics and hypothese.

        Args:
            metrics (list[MetricBase]): Metric list.
            source (list[str]): Source sentences.
            hypotheses (list[list[str]]]): Hypotheses sentences.
                The shape is (num_systems, num_sentences).
        '''
        srcs = self.srcs
        hyps = self.hyps
        
        for metric in metrics:
            scores = dict()
            if 'LLMKobayashi' not in metric.__class__.__name__:
                scores['default'] = metric.rank_systems(
                    srcs, hyps, aggregation='default'
                )
            scores['trueskill'] = metric.rank_systems(
                srcs, hyps, aggregation='trueskill'
            )
            self.save_json(
                scores, f'{metric.__class__.__name__}.json'
            )
        return scores
    
    def latexfy(
        self,
        scores: dict[str, dict[str, list[float]]],
        sys_names: list[str] = None
    ):
        '''Convert the score dictionary to the LaTex table.
        '''
        num_systems = len(list(scores.values())[0]['trueskill'])
        if sys_names is None:
            sys_names = [f"Sys{i}" for i in range(num_systems)]
        assert len(sys_names) == num_systems, f"{len(sys_names)=}, {num_systems=}"
        
        table = []
        for sys_id in range(num_systems):
            elems = [sys_names[sys_id]]
            for metric_name, score_dict in scores.items():
                if 'default' in score_dict:
                    # elems.append(f"{score_dict['default'][sys_id]:.3f}".replace('0.', '.'))
                    elems.append(score_dict['default'][sys_id])
                # else:
                    # elems.append(f"{score_dict['trueskill'][sys_id]:.3f}".replace('0.', '.'))
                elems.append(score_dict['trueskill'][sys_id])
            # line = ' & '.join(elems) + '\\\\'
            table.append(elems)

        # Annotate bold and underline
        num_row = len(table)
        num_col = len(table[0])
        for col_id in range(1, num_col):
            scores = [table[row_id][col_id] for row_id in range(num_row)]
            sorted_s = sorted(scores, reverse=True)
            for row_id in range(num_row):
                if isinstance(table[row_id][col_id], int):
                    elem = str(table[row_id][col_id])
                elif isinstance(table[row_id][col_id], float):
                    elem = f"{table[row_id][col_id]:.3f}".replace('0.', '.')
                else:
                    elem = table[row_id][col_id]

                if table[row_id][col_id] == sorted_s[0]:
                    table[row_id][col_id] = f"\\textbf{{{elem}}}"
                elif table[row_id][col_id] == sorted_s[1]:
                    table[row_id][col_id] = f"\\underline{{{elem}}}"
                else:
                    table[row_id][col_id] = elem
        lines = [' & '.join(elems) + ' \\\\' for elems in table]
        latex_table = '\n'.join(lines)
        return latex_table
    
    def latexfy_transpose(
        self,
        scores: dict[str, dict[str, list[float]]],
        sys_names: list[str] = None
    ):
        '''Convert the score dictionary to the LaTex table.
        '''
        num_systems = len(list(scores.values())[0]['trueskill'])
        if sys_names is None:
            sys_names = [f"Sys{i}" for i in range(num_systems)]
        assert len(sys_names) == num_systems, f"{len(sys_names)=}, {num_systems=}"
        num_metrics = len(scores)
        
        # (num_systems, num_metrics)
        table = [[None] + [0 for _ in range(num_systems)] for _ in range(num_metrics)]
        for sys_id in range(num_systems):
            for metric_id, (metric_name, score_dict) in enumerate(scores.items()):
                table[metric_id][0] = metric_name.split('/')[-1]
                # if 'default' in score_dict:
                #     table[metric_id][sys_id+1] = score_dict['default'][sys_id]
                table[metric_id][sys_id+1] = score_dict['trueskill'][sys_id]


        # Annotate bold and underline
        num_row = len(table)
        num_col = len(table[0])
        for row_id in range(num_row):
            scores = [table[row_id][col_id] for col_id in range(1, num_col)]
            sorted_s = sorted(scores, reverse=True)
            for col_id in range(1, num_col):
                if isinstance(table[row_id][col_id], int):
                    elem = str(table[row_id][col_id])
                elif isinstance(table[row_id][col_id], float):
                    elem = f"{table[row_id][col_id]:.3f}".replace('0.', '.')
                else:
                    elem = table[row_id][col_id]

                if table[row_id][col_id] == sorted_s[0]:
                    table[row_id][col_id] = f"\\textbf{{{elem}}}"
                elif table[row_id][col_id] == sorted_s[1]:
                    table[row_id][col_id] = f"\\underline{{{elem}}}"
                else:
                    table[row_id][col_id] = elem
        lines = [' & '.join(elems) + ' \\\\' for elems in table]
        latex_table = '\n'.join(lines)
        return latex_table
    
    def save_json(self, obj, name='data.json'):
        path = self.base_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        json.dump(obj, path.open('w'), indent=2)

    def load_json(self, name='data.json'):
        path = self.base_path / name
        data = json.load(path.open())
        return data