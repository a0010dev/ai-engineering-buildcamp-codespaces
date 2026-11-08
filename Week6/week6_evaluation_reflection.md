# Week 6 — Evaluating a recipe assistant and improving an LLM judge

During Week 6 of the AI Engineering Buildcamp, I evaluated a recipe assistant
built with **PydanticAI** and **gpt-4o-mini**, using a fixed collection of
**15 recipes**. I created **20 scenarios**, ran the agent on them, reviewed the
responses manually, and compared my labels with an LLM judge.

The scenario framework helped me move beyond straightforward recipe requests.
I covered different topics, varied the phrasing, and tested missing information,
unsupported substitutions, dietary questions, and explicit recipe restrictions.
This made the evaluation more useful than repeatedly asking questions the
assistant was likely to answer correctly.

The almond milk question showed why a plausible answer is not necessarily a
correct answer for this system. The pancake recipe lists milk but says nothing
about substitutions. The agent recommended almond milk without calling either
tool, and also claimed it did not have the recipe. I labeled the response
**bad**, and the judge agreed. The issue was not whether almond milk could work
in practice: the answer went beyond the available recipe data. Registering tools
and asking the model to use them did not guarantee that it would consult them.

I adapted the batch runner to use threads and save responses, tool calls and
returns, message history, token usage, execution time, and estimated cost. A
Jupyter notebook with **Good/Bad** buttons let me review each response, add notes,
and save labels separately. Inspecting the retrieved context helped distinguish
an unsupported answer from a failed search or an appropriate refusal. Each
scenario ran independently, so the follow-up question without a named recipe
needed clarification rather than an answer inferred from the previous CSV row.

The first judge disagreed with my labels on **3 of 20 scenarios**. Its accuracy
was **85%**, precision was **57.14%**, and recall was **100%**, treating **bad** as
the positive class. All three disagreements were false positives. Two exposed
an important setup problem: the judge was asked to detect hallucinations but
received only the question and answer, without the recipe evidence. It flagged
recipes and ingredients that were actually present in the tool results.

I added the tool calls and returns to the judge's input and updated its prompt
with general rules about evidence, faithful summaries, and offers to continue
helping. I kept the human labels out of that input. In the final saved run,
disagreements fell from **3 to 2**, accuracy increased to **90%**, and precision
increased to **66.67%**, while recall stayed at **100%**. Intermediate runs varied,
so a prompt change alone was not proof of improvement. The remaining
disagreements penalized an appropriate admission of missing calorie information
and a request for clarification.

For the bonus exercise, I used Pydantic structured output to generate **five
questions per recipe**, covering factual, how-to, detail, substitution, and
comparison questions. The judge labeled **34 of the 75 synthetic responses as
bad (45.33%)**, compared with **6 of 20 manual scenarios (30%)** using the improved
judge. All **15 substitution responses** were labeled bad. The synthetic set
also exposed invented serving quantities, undocumented baking adjustments for
smaller cakes, and missed opportunities to answer comparisons using recipe data.
These are judge decisions rather than verified error rates, and the datasets
have different question mixes, so the percentages are not a controlled measure
of a change in agent performance.

My main takeaway is that the evaluator needs evaluation too. A strict prompt
cannot compensate for missing evidence, and agreement with human labels is
something to measure rather than assume. For my capstone, I will combine
manually reviewed scenarios with synthetic questions, preserve the evidence
behind each response, and inspect disagreements before changing the judge. I
will also test prompt revisions on fresh examples to check whether the changes
generalize beyond the scenarios used to develop them.

Batch runner: [`run_scenarios.py`](run_scenarios.py)

Review notebook: [`review_results.ipynb`](review_results.ipynb)

Judge: [`judge.py`](judge.py)

Synthetic comparison: [`synthetic_comparison.json`](synthetic_comparison.json)

Course: <https://maven.com/alexey-grigorev/from-rag-to-agents>
