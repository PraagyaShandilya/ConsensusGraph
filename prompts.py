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
"""

CON_PROMPT = """
{prompt}

Use this guidance and the search results to build a strong argument against:
{task}

Search results:
{search_results}
"""

FINAL_PROMPT = """
You are an orchestrator that combines two perspectives into one balanced final answer.

Task:
{task}

Pro argument:
{pro_argument}

Con argument:
{con_argument}

Synthesize both sides and provide:
1) a concise summary of strongest pro points,
2) a concise summary of strongest con points,
3) a final recommendation with clear reasoning and trade-offs.
"""