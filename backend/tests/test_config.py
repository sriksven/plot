from backend import config


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")
    s = config.load_settings()
    assert s.openai_api_key == "sk-test"
    assert s.model == "gpt-4o"
    assert s.max_raw_rows == 1000
    assert s.price_prompt_per_1k > 0
