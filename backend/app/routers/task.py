from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.utils.http_client import call_generate, call_result

router = APIRouter(prefix="/task", tags=["Task"])

class GenerateRequest(BaseModel):
    prompt: str

@router.post("/generate")
def generate_task(req: GenerateRequest):
    return call_generate(req.prompt)

@router.get("/result/{task_id}")
def get_result(task_id: str):
    return call_result(task_id)
