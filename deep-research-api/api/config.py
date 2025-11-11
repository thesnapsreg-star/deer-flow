"""API Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_workers: int = 1

    # LLM Configuration
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    google_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None

    # Research Configuration
    default_max_step_num: int = 5
    default_max_plan_iterations: int = 1
    enable_clarification: bool = True
    enable_background_investigation: bool = True

    # Model Configuration
    coordinator_model: str = "gpt-4o-mini"
    planner_model: str = "gpt-4o"
    researcher_model: str = "gpt-4o-mini"
    coder_model: str = "gpt-4o-mini"
    reporter_model: str = "gpt-4o"
    background_investigator_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
