# Reproduction of our experiments

# Obtain attack results
We provide official attack results in [attack_results/](./attack_results/).

To reproduce these results, use `scripts/attack.py`.  
Here is an exmaple of Scribendi attack using BEA19 development set.
```sh
python scripts/attack.py \
    --att_id scribendi \
    --data bea19-dev \
    --out bea19-dev-attack.txt \
    --corpus fce-train lang8-train wi-locness-train nucle-train
```

For SOME and IMPARA, you have to set `--corpus`.
- In our settings, Adversarial-SOME uses BEA19-train = `--corpus fce-train lang8-train wi-locness-train nucle-train`.
- Adversarial-IMPARA uses BEA19-train + Troy = `--corpus fce-train lang8-train wi-locness-train nucle-train troy-1bw-train troy-blogs-train`.
```sh
python scripts/attack.py \
    --att_id some \  # or IMPARA
    --data bea19-dev \
    --out bea19-dev-attack.txt \
    --corpus fce-train lang8-train wi-locness-train nucle-train
```

The `--data` and `--corpus` can be ids listed in [gec-datasets](https://github.com/gotutiyan/gec-datasets). The dataset will be downloaded automatically, but you have to do specific pre-downloading for non-public datasets (See [HERE](https://github.com/gotutiyan/gec-datasets#non-public-datasets)).

Also, The Pillars experimets (like Table 1) should be `--data bea19-dev` and SEEDA experiments (like Table 6) should be `--data conll14`.

# Benchmark classes

The Benchmark class helps simplify and ensure fairness in experiments by fixing the system set. Required data is automatically downloaded.

- `benchmark.BenchmarkPillars` uses 10 systems introduced by [[Omelianchuk+ 24]](https://aclanthology.org/2024.bea-1.3) and our 4 attacks, thus 14 systems in total. This corresponds to Table 1.
- `benchmark.BenchmarkSEEDA` uses 14 systems introduced by [[Kobayashi+ 24]](https://aclanthology.org/2024.tacl-1.47/) and our 4 attacks, thus 18 systems in total. This corresponds to Table 6 in appendix.

```python
from benchmark import BenchmarkPillars
from gec_metrics.metrics import SOME, Scribendi, IMPARA
bench = BenchmarkPillars('exp-outputs')  # pass the output direcotory
metrics = [SOME(), Scribendi(), IMPARA()]  # load three metrics
all_scores = bench.run(metrics)

'''Now, the `all_scores` contains
{
    'SOME': {'default': [scores], 'trueskill': [scores]},
    'Scribendi': {'default': [scores], 'trueskill': [scores]},
    'IMPARA': {'default': [scores], 'trueskill': [scores]},
}
'''
```

You can also load the benchmark classes via `benchmark.get_bench()`. Note that this returns a class, not an instance.
```python
from benchmark import get_bench, get_bench_ids
# Check which ids are available
print(get_bench_ids())
# When loading Scribendi attacker
bench = get_bench('pillars')()  # The last () creates instance
# After that, you can use the attacker with the above usage.
```

Also, the results are automatically saved to `exp-outputs/<benchmark class name>/<metric class name>.json`.  
```
exp-outputs/BenchmarkPillars/
├── IMPARA.json
├── Scribendi.json
└── SOME.json
```

Each JSON contains the scores for the system set defined in the Benchmark class. The order is the same as `<benchmark class>.load_name()`. `"default"` means the absolute evaluation results, and `"trueskill"` means relative evaluation results.
```json
{
  "default": [
    0.7301861472267668,
    0.755412399603288,
    0.7529376275967353,
    0.7072013864198045,
    0.7057650593722057,
    0.7628872469430442,
    0.7581891099480543,
    0.7152791673424141,
    0.7365532071802272,
    0.7233564502475862,
    0.0,
    0.5866720086058951,
    0.9108207118090625,
    0.0
  ],
  "trueskill": [
    -0.05465021412280725,
    -0.02633036864197233,
    -0.02676351141859121,
    -0.08074192318591242,
    -0.07766374154894166,
    -0.008299499474446968,
    -0.0167023759941107,
    -0.06357101767053447,
    -0.04797522352252909,
    -0.05790509832207754,
    -1.0784671627969349,
    -0.2164105722696627,
    0.3842368075027033,
    -1.0784723680634158
  ]
}
```

For the LLM-based metrics, do `.subsetalize()` before calling `.run()`. This converts the data into subset and reduces experimental costs.
```python
from attack_gec_metrics import BenchmarkPillars
from gec_metrics import LLMKobayashi24HFSent
bench = BenchmarkPillars('exp-outputs')
metrics = [LLMKobayashi24HFSent()]
benchmark.subsetalize()
bench.run(metrics)
```

# Experimental code

### Table 1,3,4,5
- Compute scores for SOME, IMPARA, Scribendi

Table 1
```sh
python scripts/run_bench_non_llm.py \
    --bench pillars
```

Table 6
```sh
python scripts/run_bench_non_llm.py \
    --bench seeda
```

- Compute scores for LLM-based metrics
Table 1 (please change --metric_type and --model.)
```sh
python scripts/run_bench_llm.py \
    --metric_type hf-sent \
    --model google/gemma-3-27b-it \
    --bench pillars
```
- The output is saved to `exp-outputs/<Benchmark class>/<LLM metric class>/<LLM model name>.json`.
- `--metric_type` is one of `hf-sent, hf-edit, openai-sent, openai-edit`. `hf-` is HuggingFace models and `openai-*` is OpenAI model, and `*-sent` is LLM-S and `*-edit` is LLM-E.
- `--model` is a model ID.

Table 6
```sh
python scripts/run_bench_llm.py \
    --bench seeda \
    --model google/gemma-3-27b-it \
    --bench pillars
```

After all scoring done, you can generate LaTex table via `scripts/gen_table.py`.

### Table 2 (ensemble results)

Use `.ensemble()` method of the benchmark class. Here is a simple example:

```python
from benchmark import BenchmarkPillars
from gec_metrics.metrics import SOME, Scribendi, IMPARA
bench = BenchmarkPillars('toy-outputs')  # pass the output direcotory
metrics = [SOME(), Scribendi(), IMPARA()]  # load three metrics
all_scores = bench.run(metrics)

'''Now, the `all_scores` contains
{
    'SOME': {'default': [scores], 'trueskill': [scores]},
    'Scribendi': {'default': [scores], 'trueskill': [scores]},
    'IMPARA': {'default': [scores], 'trueskill': [scores]},
}
'''
ens_scores = bench.ensemble(all_scores)
'''Now, the `ens_scores` contains only ensemble results
{
    'ensemble': {'default': [scores], 'trueskill': [scores]},
}
'''

# Show LaTeX table
print(bench.latexfy(ens_scores))
```