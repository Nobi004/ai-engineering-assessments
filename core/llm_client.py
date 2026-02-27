from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from core.config import settings
from core.exceptions import LLMError
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

class LLMClient:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=0,
            api_key=settings.openai_api_key,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def structured_call(self, system_prompt: str, user_input: str, output_schema: type[BaseModel]) -> BaseModel:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        messages = [
            SystemMessage(content=system_prompt + "\n\n" + parser.get_format_instructions()),
            HumanMessage(content=user_input)
        ]
        try:
            response = await self.llm.ainvoke(messages)
            parsed = parser.parse(response.content)
            logger.info("llm_structured_call_success", model=settings.llm.model, tokens=response.usage_metadata)
            return parsed
        except Exception as e:
            logger.error("llm_call_failed", error=str(e))
            raise LLMError(f"LLM call failed: {str(e)}")