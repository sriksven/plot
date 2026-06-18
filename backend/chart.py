"""Build a Plotly-friendly chart spec from a query result.

A chart needs exactly 2 columns: a category/x and a numeric/y. Otherwise 'none'.
"""


def build_chart_spec(chart_type: str, columns: list, rows: list) -> dict:
    if chart_type == "none" or len(columns) != 2 or not rows:
        return {"type": "none"}
    x = [r[0] for r in rows]
    y = [r[1] for r in rows]
    return {
        "type": chart_type if chart_type in ("bar", "line", "pie") else "bar",
        "x": x,
        "y": y,
        "x_label": columns[0],
        "y_label": columns[1],
    }
