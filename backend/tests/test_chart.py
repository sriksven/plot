from backend.chart import build_chart_spec


def test_bar_chart_spec():
    spec = build_chart_spec(
        chart_type="bar",
        columns=["county", "n"],
        rows=[["los angeles", 2851925], ["orange", 728565]],
    )
    assert spec["type"] == "bar"
    assert spec["x"] == ["los angeles", "orange"]
    assert spec["y"] == [2851925, 728565]


def test_none_chart_returns_none_type():
    spec = build_chart_spec("none", ["a"], [[1]])
    assert spec["type"] == "none"


def test_falls_back_to_none_when_not_two_columns():
    spec = build_chart_spec("bar", ["a", "b", "c"], [[1, 2, 3]])
    assert spec["type"] == "none"
