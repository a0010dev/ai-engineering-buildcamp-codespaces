# Week 6: running evaluation scenarios

From the repository root, using the project's Python environment:

```bash
.venv/bin/python Week6/run_scenarios.py --workers 4
```

Reads `Week6/scenarios.csv` and saves `Week6/results.json`. You can change the
paths with `--input` and `--output`, and run a small batch with `--limit 2`.
Set `OPENAI_API_KEY` in the environment to run the real agent.

The runner uses `ThreadPoolExecutor` and `as_completed`, preserves CSV order,
and captures errors for each scenario. If `tqdm` is available, it displays a
progress bar; otherwise, it displays a counter. Each call has its own HTTP
client and independent conversation.

Results include the response, tool calls and returns, messages, tokens,
execution time, and estimated cost using the rates already defined in the
runner. `status=ok` indicates successful execution, not a correct response.
Failed runs record the exception class and `cost=null`; they may have incurred
charges before failing. The output file is overwritten on each run.

The current `context-dependent` scenario runs without message history, just
like the others. To evaluate conversation memory, prepare an initial question
and pass its message history to the next turn.

Local tests, without API calls:

```bash
.venv/bin/python -m unittest discover -s Week6 -p 'test_*.py'
```

## Manual review

Open `Week6/review_results.ipynb` in Jupyter or VS Code and select the kernel
from the project's `.venv`. Run the cells in order. The **Good** and **Bad**
buttons save each label and optional note to `Week6/labels.json`, then advance
to the next unreviewed scenario. You can inspect the retrieved tool context
and navigate with **Anterior** (Previous) and **Següent** (Next) to correct labels.

Review resumes when you rerun the notebook. If `results.json` has changed,
archive the labels or choose a different `LABELS_PATH` to start a new review.
The notebook makes no API calls and does not modify `results.json`.

## Synthetic dataset (bonus)

Generate 5 questions per recipe using Pydantic structured output, run the
agent, and evaluate all 75 responses with the improved judge's prompt:

```bash
.venv/bin/python Week6/generate_scenarios.py
.venv/bin/python Week6/run_scenarios.py --input Week6/synthetic_scenarios.csv --output Week6/synthetic_results.json --workers 4
.venv/bin/python Week6/judge.py --input Week6/synthetic_results.json --output Week6/synthetic_results_judged.json
.venv/bin/python Week6/compare_synthetic.py
```

The first three commands make API calls and incur charges. The comparison
saves `Week6/synthetic_comparison.json` with the overall percentage of `bad`
labels and a breakdown by question type. These are judge decisions, not human
labels; the two datasets cover different question types. Synthetic files are
overwritten if you rerun the commands; manual results are preserved.
