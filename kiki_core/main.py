import re
import sys
import os

#import pysqlite3
#sys.modules["sqlite3"] = pysqlite3

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

from .parent.parent_agent import run_kiki_orchestrator

app = FastAPI(
    title="kiki API",
    description="CrewAI (Parent) on Azure App Service",
    version="0.1.0",
    openapi_version="3.0.2"
)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

EXPECTED_API_KEY = os.getenv("API_KEY")


async def get_api_key(api_key_header: str = Security(api_key_header)):
    """APIキーを検証する関数"""
    if not EXPECTED_API_KEY:
        print("CRITICAL WARNING: API_KEY is not set in Environment Variables!")

    if api_key_header == EXPECTED_API_KEY:
        return
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials"
        )


class UserRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {"message": "kiki parent agent is running"}


@app.post("/ask", response_model=AgentResponse, dependencies=[Depends(get_api_key)])
def ask_kiki(req: UserRequest):
    """
    Copilot Studio から叩かれるエンドポイント
    """
    try:
        # 親エージェントを起動
        result = run_kiki_orchestrator(req.query)

        raw_text = result.raw
        match = re.search(r"<RESULT>(.*?)</RESULT>", raw_text, re.DOTALL)
        if match:
            final_response = match.group(1).strip()
        else:
            final_response = raw_text

        return {"response": final_response}

    except Exception as e:
        return {"response": f"[ERROR] {e}"}

