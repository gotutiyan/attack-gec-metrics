# hacking-gec-metrics

This is the official repository of the following paper:
```
```

# Install

```sh
pip install git+https://github.com/naist-nlp/attack-gec-metrics
```

Or 
```sh
git clone https://github.com/naist-nlp/attack-gec-metrics.git
cd attack_gec_metrics
pip install -e ./
```

UV user can `uv add git+https://github.com/naist-nlp/attack-gec-metrics`.

# Components

## Attackers

- `attack_gec_metrics.AtackerForSOME` is an attack on SOME metric.
- `attack_gec_metrics.AttackerForScribendi` is an attack on Scribendi metric.
- `attack_gec_metrics.AttackerForIMPARA` is an attack on IMPARA metric.
- `attack_gec_metrics.AttackerForLLMSent` is an attack on LLM-S metric.

All attackers can be used with the unified interface. This is an example to use `AttackerForScribendi`.
```python
from attack_gec_metrics.attackers import AttackerForScribendi
from gec_datasets import GECDatasets
srcs = GECDatasets('exp-datasets').load('bea19-dev').srcs[:5]
attacker = AttackerForScribendi()
attacker.config.verbose = True
# All Attacker classes have .correct() to obtain attack results.
attack_hyps = attacker.correct(srcs)

for i in range(5):
    print('Source:       ', srcs[i])
    print('Attack result:', attack_hyps[i])
    print()
```

Our results are in here: [attack_results/](./attack_results/).

All classes are implemented based on `attack_gec_metrics.AttackerBase`. You can use this class to build your custom attack class.

```python
# An example to build your custom attacker.
from attack_gec_metrics import AttackerBase

class CustomAttacker(AttackerBase):
    def __init__(self, config=None):
        super().__init__(config)
    
    def correct(self, sources: list[str]) -> list[str]:
        raise NotImplementedError
```

## Benchmark

The benchmark class simplifies experimentation by providing a fixed system output. All necessary data will be automatically downloaded.

- `attack_gec_metrics.BenchmarkPillars` corresponds to Table 1.
- `attack_gec_metrics.BenchmarkSEEDA` corresponds to Table 6 (in appendix).


```python
from attack_gec_metrics import BenchmarkPillars
from gec_metrics import SOME, Scribendi, IMPARA
bench = BenchmarkPillars('exp-outputs')  # pass the output direcotory
metrics = [SOME(), Scribendi(), IMPARA()]
bench.run(metrics)

## Get srcs, hyps
# bench.srcs  # (num_sents,)
# bench.hyps  # (num_systems, num_sents)

## to get system names:
# names: list[str] = bench.load_names()  # shape is (num_systems). The order is the same as bench.load_hyps() results.

## to make subset for LLM-evaluation:
# bench.subsetalize()  # returns nothing but the bench.srcs and bench.hyps are now subset.
```

After that, the results are saved to `exp-outputs/<benchmark class name>/{SOME | Scribendi | IMPARA}.json`. Each JSON contains the scores for the system set defined in the Benchmark class. The order is the same as `<benchmark class>.load_name()`.

```
exp-outputs/BenchmarkSEEDA/
├── IMPARA.json
├── Scribendi.json
└── SOME.json
```

More detailed experimental code can be found in [experiments/](./experiments/) .