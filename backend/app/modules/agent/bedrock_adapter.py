from langchain_aws import ChatBedrock

from app.config import settings
from app.modules.agent.llm_adapter import LLMProviderAdapter


class BedrockAdapter(LLMProviderAdapter):
    def get_chat_model(self) -> ChatBedrock:
        return ChatBedrock(
            model_id=settings.BEDROCK_MODEL_ID,
            region_name=settings.AWS_REGION,
        )
