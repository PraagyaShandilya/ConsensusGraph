SYS_PROMPT = """
You are a research planner. Given a task, produce:
1) a focused prompt for a pro-argument researcher,
2) 3-5 search topics that support the pro side,
3) a focused prompt for a con-argument researcher,
4) 3-5 search topics that support the con side.
Keep prompts actionable and evidence-focused.
"""

FOR_PROMPT = """
{prompt}

Use this guidance and the search results to build a strong argument in support of:
{task}

Search results:
{search_results}

Requirements:
- Use evidence from the search results.
- Cite claims inline using bracketed source numbers like [1], [2].
- Only cite numbers that appear in the provided search results.
"""

CON_PROMPT = """
{prompt}

Use this guidance and the search results to build a strong argument against:
{task}

Search results:
{search_results}

Requirements:
- Use evidence from the search results.
- Cite claims inline using bracketed source numbers like [1], [2].
- Only cite numbers that appear in the provided search results.
"""

FINAL_PROMPT = """
You are an orchestrator that combines two perspectives into one balanced final answer.

Task:
{task}

Pro argument:
{pro_argument}

Pro rebuttal:
{pro_rebuttal}

Con argument:
{con_argument}

Con rebuttal:
{con_rebuttal}

Available citations:
{citations}

Synthesize both sides and provide:
1) a concise summary of strongest pro points (including rebuttals),
2) a concise summary of strongest con points (including rebuttals),
3) a final recommendation with clear reasoning and trade-offs.

Requirements:
- Add inline citations like [1], [2] for factual claims.
- Only use citations from the provided citation list.
"""

REBUTTAL_PROMPT = """
You are a researcher defending the **{side}** position on: {task}

Your initial argument:
{own_argument}

Opposing argument to rebut:
{opposing_argument}

Critically analyze the opposing argument. Identify its weakest claims or contradictions, and write a sharp rebuttal that strengthens your overall position.
"""