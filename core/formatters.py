def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0


def direction(value: float, is_money: bool = False, is_pct: bool = False) -> str:
    arrow = "▲" if value > 0 else "▼" if value < 0 else "—"
    if is_money:
        return f"{arrow} {money(abs(value))}"
    if is_pct:
        return f"{arrow} {abs(value):.1%}"
    return f"{arrow} {value}"


def md_to_html(text: str) -> str:
    html = text.replace("\n\n", "</p><p>").replace("\n", "<br>")
    return f"<p>{html}</p>"
