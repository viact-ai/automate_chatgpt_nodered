import os

import dotenv

dotenv.load_dotenv()


class Config:
    def __init__(self) -> None:
        self.debug_mode = False
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.node_red_server = os.getenv("NODE_RED_SERVER", "")
        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")
        self.temperature = float(os.getenv("TEMPERATURE", "1"))

        assert self.openai_api_key != "", "OpenAI API key not found"
