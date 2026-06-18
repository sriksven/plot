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
    # join-requiring
    "What is the average age of victims in fatal collisions, by county? Top 5.",
    # CTE-requiring
    "Among counties with over 100000 collisions, which has the highest share "
    "of motorcycle crashes? Use a CTE.",
]


def test_join_question_produces_join():
    result = pipeline.answer_question(
        "What is the average victim age in alcohol-involved collisions, by county? Top 5."
    )
    assert result.error is None, result.error
    assert "join" in result.sql.lower()
    assert len(result.rows) > 0


def test_cte_question_produces_cte():
    result = pipeline.answer_question(
        "Using a CTE, find the county with the highest fatal-crash rate "
        "among counties with more than 50000 collisions."
    )
    assert result.error is None, result.error
    assert "with" in result.sql.lower()
    assert len(result.rows) > 0


@pytest.mark.parametrize("q", GOLDEN)
def test_golden_question_returns_rows(q):
    result = pipeline.answer_question(q)
    assert result.error is None, f"{q}: {result.error}"
    # a read-only query is either a plain SELECT or a CTE (WITH ...)
    assert result.sql.lower().lstrip().startswith(("select", "with"))
    assert len(result.rows) > 0


def test_la_is_top_county():
    result = pipeline.answer_question("Which county has the most collisions?")
    assert "los angeles" in str(result.rows[0]).lower()
