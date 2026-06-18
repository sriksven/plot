from backend.data_dictionary import build_schema_prompt


def test_schema_prompt_mentions_tables_and_encodings():
    p = build_schema_prompt()
    for table in ["collisions", "parties", "victims", "case_ids"]:
        assert table in p
    # key grounding facts the model needs
    assert "parked motor vehicle" in p
    assert "alcohol_involved" in p
    assert "fatal" in p
    assert "case_id" in p  # join key
