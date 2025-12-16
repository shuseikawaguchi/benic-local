from fastapi import FastAPI
from kiki_core.parent.parent_agent import run_kiki_orchestrator
from pydantic import BaseModel

app = FastAPI(
    title="kiki API",
    description="CrewAI (Parent) on Azure App Service",
    version="0.1.0",
    openapi_version="3.0.2"
)


class UserRequest(BaseModel):
    query: str

#class UserRequest(BaseModel):
#    text: str                 # ユーザーの自然文
#    context: dict | None = None  # Copilot Studio等から渡る補助情報


@app.get("/")
def root():
    return {"message": "kiki parent agent is running"}


@app.post("/ask")
def ask_kiki(req: UserRequest):
    try:
        # 親エージェントを起動
        result = run_kiki_orchestrator(req.query)
        
        # ★修正: 正規表現(re)は削除！ シンプルに Pydantic の中身を取り出すだけ。
        # output_pydantic を使った場合、result.pydantic にデータが入っています。
        final_response = result.pydantic.tool_response
        
        return {"response": final_response}
        
    except Exception as e:
        return {"error": str(e)}
    