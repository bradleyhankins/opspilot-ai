def build_manager_prompt(rules_brief: str, metrics: dict, targets: dict) -> str:
    return f"""
You are an operations and sales performance manager.
Turn the rules-based brief into a concise manager-ready memo.
Use only the provided data. Do not invent numbers, names, or causes.
Keep it practical and action-oriented.

Metrics:
{metrics}

Targets:
{targets}

Rules-based manager brief:
{rules_brief}

Return:
1. Executive summary
2. What changed
3. Primary bottleneck
4. Coaching focus
5. Lead source focus
6. Three manager action items
"""
