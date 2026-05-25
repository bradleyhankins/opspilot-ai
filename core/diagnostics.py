import pandas as pd

from core.formatters import money, safe_divide


def evaluate_metric(value: float, target: float, metric_name: str) -> tuple[str, str, str]:
    if value >= target:
        return "Healthy", "status-healthy", f"{metric_name} is meeting or exceeding the target."
    if value >= target * 0.85:
        return "Watch", "status-medium", f"{metric_name} is close to target but should be watched."
    return "Risk", "status-high", f"{metric_name} is materially below target and needs manager attention."


def generate_diagnosis(metrics: dict, targets: dict, rep_summary: pd.DataFrame, source_summary: pd.DataFrame) -> dict:
    metric_checks = [
        ("Demo Rate", metrics["demo_rate"], targets["demo_rate"]),
        ("Close Rate", metrics["close_rate"], targets["close_rate"]),
        ("Average Sale", metrics["avg_sale"], targets["avg_sale"]),
        ("NSLI", metrics["nsli"], targets["nsli"]),
    ]
    metric_gaps = [(name, safe_divide(target - value, target)) for name, value, target in metric_checks]
    primary_bottleneck, primary_gap = max(metric_gaps, key=lambda item: item[1])

    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    review_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    review_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]

    if primary_gap <= 0:
        primary_bottleneck = "No Critical Bottleneck"
        priority = "Healthy"
        likely_cause = "The selected data is meeting the configured targets."
        manager_action = "Study the top rep and strongest lead source, then document the behaviors that should become the team standard."
        coaching_move = "Use coaching time for advanced skill sharpening rather than basic correction."
        roleplay = "Customer says: 'Everything sounds good, but I want to make sure we are making the right decision.'"
    elif primary_bottleneck == "Demo Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is not converting enough issued leads into completed demos."
        manager_action = "Review no-demo leads by rep and lead source. Tighten appointment confirmation and expectation setting."
        coaching_move = "Coach reps on decision-maker confirmation, urgency, and reducing no-show risk."
        roleplay = "Customer says: 'Just come out and give me a quick quote.'"
    elif primary_bottleneck == "Close Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is getting demos but not converting enough into sales."
        manager_action = "Review recent unsold demos and identify the most common objection."
        coaching_move = "Coach discovery, value build, urgency, and direct commitment language."
        roleplay = "Customer says: 'We need to think about it and get a few more quotes.'"
    elif primary_bottleneck == "Average Sale":
        priority = "Medium"
        likely_cause = "The team is closing work, but project size is below target."
        manager_action = "Audit sold scopes for missed upgrades, add-ons, and incomplete value presentation."
        coaching_move = "Coach good/better/best options and complete scope positioning."
        roleplay = "Customer says: 'We just want the cheapest option that gets the job done.'"
    else:
        priority = "Medium"
        likely_cause = "Revenue per issued lead is below target."
        manager_action = "Compare NSLI by rep and lead source and reallocate focus toward stronger channels."
        coaching_move = "Coach prioritization, speed-to-lead, and conversion discipline."
        roleplay = "Customer says: 'I’m not sure if this is something we’re ready to do right now.'"

    return {
        "primary_bottleneck": primary_bottleneck,
        "priority": priority,
        "likely_cause": likely_cause,
        "manager_action": manager_action,
        "coaching_move": coaching_move,
        "roleplay": roleplay,
        "best_rep": best_rep,
        "review_rep": review_rep,
        "best_source": best_source,
        "review_source": review_source,
    }


def build_priorities(diagnosis: dict, metrics: dict, targets: dict) -> list[str]:
    priorities = [
        f"Coach {diagnosis['review_rep']['Rep']} around {diagnosis['primary_bottleneck']} and review their next 3 opportunities.",
        f"Audit {diagnosis['review_source']['Lead Source']} lead quality before increasing spend or activity there.",
        f"Protect {diagnosis['best_source']['Lead Source']} and study why it is producing stronger NSLI.",
    ]
    if metrics["demo_rate"] < targets["demo_rate"]:
        priorities[0] = "Review no-demo leads and tighten appointment confirmation/expectation setting."
    if metrics["close_rate"] < targets["close_rate"]:
        priorities[0] = "Review unsold demos and roleplay the most common closing objection this week."
    return priorities[:3]


def rep_coaching_note(row: pd.Series, targets: dict) -> list[str]:
    notes = []
    if row["Demo Rate"] < targets["demo_rate"]:
        notes.append("Demo rate is below target; coach confirmation and lead commitment.")
    if row["Close Rate"] < targets["close_rate"] and row["Demos"] >= 1:
        notes.append("Close rate is below target; coach value build and objection handling.")
    if row["Average Sale"] < targets["avg_sale"] and row["Sales"] >= 1:
        notes.append("Average sale is below target; review scope completeness and upgrade positioning.")
    if row["NSLI"] < targets["nsli"]:
        notes.append("NSLI is below target; review lead quality, conversion discipline, and follow-up speed.")
    return notes or ["Performance is healthy against current targets; study and document what is working."]


def operational_health_status(metrics: dict, targets: dict) -> str:
    checks = [
        metrics["demo_rate"] >= targets["demo_rate"],
        metrics["close_rate"] >= targets["close_rate"],
        metrics["avg_sale"] >= targets["avg_sale"],
        metrics["nsli"] >= targets["nsli"],
    ]
    passed = sum(checks)
    if passed >= 3:
        return "Stable"
    if passed == 2:
        return "Watch"
    return "Needs Attention"


def best_manager_move(diagnosis: dict) -> str:
    if diagnosis["primary_bottleneck"] == "Demo Rate":
        return "Tighten confirmation and appointment-setting standards."
    if diagnosis["primary_bottleneck"] == "Close Rate":
        return "Run objection roleplay and review unsold demos."
    if diagnosis["primary_bottleneck"] == "Average Sale":
        return "Audit scopes for missed upgrades and add-ons."
    if diagnosis["primary_bottleneck"] == "NSLI":
        return "Review lead allocation and protect stronger lead sources."
    return "Document what is working and standardize it."
