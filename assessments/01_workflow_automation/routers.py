from fastapi import APIRouter, Depends
from assessments.01_workflow_automation.services import WorkflowService
from assessments.01_workflow_automation.schemas import WorkflowResponse
from core.exceptions import AppBaseException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/01-workflow", tags=["Assessment 1"])

@router.post("/leads", response_model=WorkflowResponse)
async def process_lead(raw_lead: dict):
    try:
        return await WorkflowService.process_lead(raw_lead)
    except AppBaseException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.code, "detail": str(e)}
        )