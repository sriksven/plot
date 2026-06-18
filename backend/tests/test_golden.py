import os
import pytest
from backend import pipeline

pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"), reason="needs real API key"
)

GOLDEN = [
    "Which county has the most collisions?",
    "What percentage of collisions involved a parked vehicle?",
    "How many collisions happened each day of the week?",
    "Which vehicle makes are in the most crashes?",
    "How did collisions change each year from 2018 to 2021?",
]


@pytest.mark.parametrize("q", GOLDEN)
def test_golden_question_returns_rows(q):
    result = pipeline.answer_question(q)
    assert result.error is None, f"{q}: {result.error}"
    assert result.sql.lower().startswith("select")
    assert len(result.rows) > 0


def test_la_is_top_county():
    result = pipeline.answer_question("Which county has the most collisions?")
    assert "los angeles" in str(result.rows[0]).lower()
