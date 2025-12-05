import os
from pathlib import Path

from dotenv import load_dotenv

# .env ロード
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 環境変数の強制上書き(CrewAIAzureの設定無視対策)
os.environ["OPENAI_API_KEY"] = "NA" # ダミー
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")

from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

from .children_connectors import (
    CostEstimationConnector,
    DeviationCheckConnector,
    RequirementBotConnector
)

# 出力用の箱（これはそのまま）
class AgentOutput(BaseModel):
    tool_response: str = Field(description="ツールから返ってきたテキスト全文。")


def run_kiki_orchestrator(user_input: str):
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").replace("azure/", "")

    # LLMオブジェクトの作成
    # CrewAI専用のLLMクラスを使い、model名に"azure/"を付ける
    kiki_llm = LLM(
        model=f"azure/{deployment_name}",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        temperature=0
    )

    # 親エージェント定義
    manager = Agent(
        role='kiki_router',
        goal='入力をツールに渡し、出力を抽出する',
        backstory='あなたはデータを右から左へ受け流すパイプライン処理プログラムです。人間のような会話や補足は機能として実装されていません。',
        tools=[
            RequirementBotConnector(),
            DeviationCheckConnector(),
            CostEstimationConnector()
        ],
        verbose=True,
        allow_delegation=False,
        llm=kiki_llm,
        function_calling_llm=kiki_llm
    )
# ★タスク定義を修正（タグの話を消し、コピーを徹底させる）
    task = Task(
        description=f"""
        ユーザー入力: 「{user_input}」
        
        1. 最適なツールを実行する。
        2. ツールから返ってきたテキスト（文字列）を取得する。
        3. そのテキストを、**一文字も変更・削除せず**、そのまま `tool_response` に格納する。
        
        【重要】
        - ツールが返す「【〇〇からの回答】」という部分も、大切なデータの一部です。絶対に削除してはいけません。
        - 挨拶や補足は一切禁止です。
        """,
        expected_output="ツールからの出力テキスト（完全なコピー）",
        output_pydantic=AgentOutput, # ★この「型」強制が最強の縛りです
        agent=manager
    )


    crew = Crew(
        agents=[manager],
        tasks=[task],
        process=Process.sequential
    )

    return crew.kickoff()