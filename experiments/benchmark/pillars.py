from .base import BenchmarkBase
from pathlib import Path
import subprocess

class BenchmarkPillars(BenchmarkBase):
    def __init__(self, base_path: str = 'exp-outputs'):
        super().__init__(base_path)
        self.path = self.gec.base_path / 'pillars'
        self.path.mkdir(parents=True, exist_ok=True)
        if not (self.path / 'pillars-of-gec').exists():
            subprocess.run([
                'git', 'clone', 'https://github.com/grammarly/pillars-of-gec.git',
                str(self.path / 'pillars-of-gec')
            ])
        
        self.srcs = self.gec.load('bea19-dev').srcs
        self.hyps = self.load_hyps()

    def load_path(self):
        files = list(self.path.glob('**/single_systems/*bea-dev.txt'))
        assert len(files) == 7
        files = sorted(files, key=lambda x: str(x))
        files += [
            self.path / "pillars-of-gec/data/system_preds/ensemble_systems/ens_m7___bea-dev.txt",
            self.path / "pillars-of-gec/data/system_preds/ensemble_systems/ens_greco_on_m7___bea-dev.txt",
            self.path / "pillars-of-gec/data/system_preds/ensemble_systems/ens_m9_with_greco_and_gpt___bea-dev.txt",
        ]
        files += [
            Path("attack_results/bea19-dev-some.txt"),
            Path("attack_results/bea19-dev-scribendi.txt"),
            Path("attack_results/bea19-dev-impara.txt"),
            Path("attack_results/bea19-dev-llmsent.txt"),
        ]
        return files[:]

    def subsetalize(self):
        '''Make each hypotheses subset.
        This is for LLM evaluations.
        '''
        self.subset_hyps = []
        subset_indices = list(range(400))
        self.orig_srcs = self.srcs[:]
        self.orig_hyps = self.hyps[:]
        self.srcs = [self.srcs[i] for i in subset_indices]
        self.hyps = [[hyps[i] for i in subset_indices] for hyps in self.hyps]
        return
    
    def load_name(self):
        files = self.load_path()
        name = [
            f.name.replace('___bea-dev.txt', '') \
                .replace('ens_m7', 'ENS-Voting') \
                .replace('ens_greco_on_m7', 'ENS-GRECO') \
                .replace('ens_m9_with_greco_and_gpt', 'ENS-ENS') \
                .replace('bea19-dev-some.txt', 'Attack-SOME') \
                .replace('bea19-dev-scribendi.txt', 'Attack-Scribendi') \
                .replace('bea19-dev-impara.txt', 'Attack-IMPARA') \
                .replace('bea19-dev-llmsent.txt', 'Attack-LLM')
            for f in files
        ]
        return name
    
    def load_hyps(self):
        files = self.load_path()
        hyps = [
            f.read_text().rstrip().split('\n')
            for f in files
        ]
        return hyps
