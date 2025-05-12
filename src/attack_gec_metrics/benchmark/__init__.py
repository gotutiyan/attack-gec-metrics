from .base import BenchmarkBase
from .pillars import BenchmarkPillars
from .seeda import BenchmarkSEEDA

classes = [
    BenchmarkPillars,
    BenchmarkSEEDA
]
id2class = {
    c.__name__.lower().replace('benchmark', ''): c for c in classes
}

def get_bench_ids():
    return list(id2class.keys())

def get_bench(name=None):
    if name not in get_bench_ids():
        raise ValueError(f'The name {name} is invalid. Candidates are {get_bench_ids()}.')
    return id2class[name]