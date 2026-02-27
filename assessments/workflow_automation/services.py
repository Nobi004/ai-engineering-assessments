from core.llm_client import LLMClient
from core.logger import logger
from assessments.workflow_automation.schemas import IntentClassification, LeadFields, WorkflowLead, WorkflowResponse
from core.exceptions import ValidationError, DatabaseError
from core.database import AsyncSessionLocal
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import re
from uuid import uuid4

llm = LLMClient()

class WorkflowService:
    INTENT_PROMPT = """You are a deterministic lead routing agent.
Classify the lead into exactly one: sales, support, partnership, unknown.
Return ONLY JSON with intent and confidence (0.0-1.0)."""

    EXTRACTION_PROMPT = """Extract fields from the lead message. Never invent values.
Missing fields = null. Return ONLY valid JSON matching the schema."""

    RESPONSE_PROMPT = """You are a professional sales assistant.
Use ONLY the extracted fields and intent. Write a natural, helpful reply (max 3 sentences)."""

    @staticmethod
    async def process_lead(raw_lead: dict) -> WorkflowResponse:
        request_id = str(uuid4())
        logger = structlog.get_logger().bind(request_id=request_id)

        async with AsyncSessionLocal() as session:
            try:
                # 1. Intent Classification
                intent_result: IntentClassification = await llm.structured_call(
                    WorkflowService.INTENT_PROMPT, json.dumps(raw_lead), IntentClassification
                )

                if intent_result.confidence < 0.7:
                    intent_result.intent = "unknown"

                # 2. Field Extraction
                extraction_result: LeadFields = await llm.structured_call(
                    WorkflowService.EXTRACTION_PROMPT, json.dumps(raw_lead), LeadFields
                )

                # 3. Fallback regex if critical fields missing
                if not extraction_result.email:
                    email_match = re.search(r"[\w\.-]+@[\w\.-]+", json.dumps(raw_lead))
                    if email_match:
                        extraction_result.email = email_match.group(0)

                # 4. Generate AI Response
                context = f"Intent: {intent_result.intent}\nFields: {extraction_result.model_dump_json()}"
                ai_response = await llm.llm.ainvoke([
                    SystemMessage(content=WorkflowService.RESPONSE_PROMPT),
                    HumanMessage(content=context)
                ])

                # 5. Save to DB
                lead = WorkflowLead(
                    raw_input=raw_lead,
                    intent=intent_result.intent,
                    confidence=intent_result.confidence,
                    extracted_fields=extraction_result.model_dump(),
                    ai_response=ai_response.content,
                    status="processed",
                    request_id=request_id,
                )
                session.add(lead)
                await session.commit()
                await session.refresh(lead)

                logger.info("lead_processed", lead_id=str(lead.id), intent=intent_result.intent)

                return WorkflowResponse(
                    lead_id=lead.id,
                    intent=lead.intent,
                    confidence=lead.confidence,
                    extracted_fields=LeadFields(**lead.extracted_fields),
                    ai_response=lead.ai_response or "",
                    status=lead.status,
                    execution_trace={"intent_confidence": lead.confidence, "request_id": request_id}
                )

            except Exception as e:
                await session.rollback()
                logger.error("lead_processing_failed", error=str(e), request_id=request_id)
                raise DatabaseError("Failed to process lead") from e