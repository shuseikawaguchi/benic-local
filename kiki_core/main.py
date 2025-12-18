import re
import sys

import pysqlite3

sys.modules["sqlite3"] = pysqlite3
from fastapi import FastAPI
from pydantic import BaseModel


# --- APIキー用の設定 ---
import os
from fastapi import Header, HTTPException, Depends

def verify_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv("API_KEY")

    if not expected_key:
        # 環境変数が未設定（サーバー設定ミス）
        raise HTTPException(status_code=500, detail="API_KEY is not configured")

    if x_api_key != expected_key:
        # APIキーが不一致（ユーザー側のミス）
        raise HTTPException(status_code=401, detail="Invalid API Key")
# ---   ---


from kiki_core.parent.parent_agent import run_kiki_orchestrator

app = FastAPI(
    title="kiki API",
    description="CrewAI (Parent) on Azure App Service",
    version="0.1.0",
    openapi_version="3.0.2"
)


class UserRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "kiki parent agent is running"}


@app.post("/ask")
def ask_kiki(
    req: UserRequest,
    _: None = Depends(verify_api_key),
):
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
        return {"error": str(e)}