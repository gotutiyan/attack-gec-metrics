from .base import BenchmarkBase
from pathlib import Path
import subprocess

class BenchmarkSEEDA(BenchmarkBase):
    def __init__(self, base_path: str='exp-outputs'):
        super().__init__(base_path)
        self.path = Path(self.gec.base_path)
        self.path.mkdir(parents=True, exist_ok=True)
        if not (self.path / 'SEEDA').exists():
            subprocess.run([
                'git', 'clone', 'https://github.com/tmu-nlp/SEEDA.git',
                str(self.path / 'SEEDA')
            ])
        
        self.srcs = self.gec.load('conll14').srcs
        self.hyps = self.load_hyps()

    def load_path(self):
        MODELS = [
            'BART',
            'BERT-fuse',
            'GECToR-BERT',
            'GECToR-ens',
            'GPT-3.5',
            'LM-Critic',
            'PIE',
            'REF-F',
            'REF-M',
            'Riken-Tohoku',
            'T5',
            'TemplateGEC',
            'TransGEC',
            'UEDIN-MS'
        ]
        files = [self.path / f'SEEDA/outputs/all/{m}.txt' for m in MODELS]
        files += [
            Path("attack_results/conll14-some.txt"),
            Path("attack_results/conll14-scribendi.txt"),
            Path("attack_results/conll14-impara.txt"),
            Path("attack_results/conll14-llmsent.txt"),
        ]
        return files[:]
    
    def subsetalize(self):
        '''Make each hypotheses subset.
        This is for LLM evaluations.
        '''
        self.subset_hyps = []
        sub_srcs = (self.path / f'SEEDA/outputs/subset/INPUT.txt').read_text().rstrip().split('\n')
        all_srcs = (self.path / f'SEEDA/outputs/all/INPUT.txt').read_text().rstrip().split('\n')
        subset_indices = [all_srcs.index(ss) for ss in sub_srcs]
        self.orig_srcs = self.srcs[:]
        self.orig_hyps = self.hyps[:]
        self.srcs = [self.srcs[i] for i in subset_indices]
        self.hyps = [[hyps[i] for i in subset_indices] for hyps in self.hyps]
        return
    
    def load_name(self):
        files = self.load_path()
        name = [
            f.name.replace('.txt', '') \
                .replace('conll14-some', 'Attack-SOME') \
                .replace('conll14-scribendi', 'Attack-Scribendi') \
                .replace('conll14-impara', 'Attack-IMPARA') \
                .replace('conll14-llmsent', 'Attack-LLM')
            for f in files]
        return name
    
    def load_hyps(self):
        files = self.load_path()
        hyps = [f.read_text().rstrip().split('\n') for f in files]
        return hyps
