# Obtain attack results
```sh
python scripts/attack.py \
    --att_id forscribendi \
    --data bea19-dev \
    --out output.txt
```

The candidates of `--att_id` can be found:
```python
from attack_gec_metrics import get_attacker_ids
print(get_attacker_ids())
# ['forimpara', 'forscribendi', 'forsome', 'forllmsent']
```

# Evaluate the system set

Our Benchmark** class provides fix system outputs.

For SOME, Scribendi, IMPARA:
```sh
python scripts/run_bench_non_llm.py \
    --bench pillars
```

For LLM metrics:
```sh
python scripts/run_bench_llm.py \
    --bench pillars \
    --metric_type hf-sent \
    --model Qwen/Qwen3-32B \
```

- The output is saved to `exp-outputs/<Benchmark class>/<LLM metric class>/<LLM model name>.json`.
- `--metric_type` is one of `hf-sent, hf-edit, openai-sent, openai-edit`. `hf-` is HuggingFace models and `openai-*` is OpenAI model, and `*-sent` is LLM-S and `*-edit` is LLM-E.
- `--model` is a model ID.

# Generate LaTex table
Note: This script does not output header of the table. Please refer to it as an example.

```sh
python scripts/gen_table.py 
```