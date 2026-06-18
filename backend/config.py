import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    model: str
    price_prompt_per_1k: float
    price_completion_per_1k: float
    data_dir: str
    metrics_dir: str
    max_raw_rows: int


def load_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        price_prompt_per_1k=float(os.getenv("LLM_PRICE_PROMPT_PER_1K", "0.0025")),
        price_completion_per_1k=float(os.getenv("LLM_PRICE_COMPLETION_PER_1K", "0.01")),
        data_dir=os.getenv("DATA_DIR", "data"),
        metrics_dir=os.getenv("METRICS_DIR", "metrics"),
        max_raw_rows=int(os.getenv("MAX_RAW_ROWS", "1000")),
    )
