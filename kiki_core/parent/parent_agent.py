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


class ExactOutput(BaseModel):
    result_text: str = Field(description="ツールから返ってきたテキストそのもの。一文字も変更・追加してはいけない。")


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

    task = Task(
        description=f"""
        ユーザー入力: 「{user_input}」

        【最重要指令】
        あなたは「回答生成」を行ってはなりません。あなたの仕事は「ツールの実行結果を運ぶこと」だけです。
        もしツールが「A」と返したら、あなたの答えも「A」でなければなりません。
        **追加で「〇〇をご提案します...」「を以下にまとめます」となった時点で失敗**です。

        手順:
        1. 適切なツールを実行する。
        2. ツールから返ってきたテキスト（Tool Output）をそのまま取得する。
        3. そのテキストが「作成しました」という短い報告であっても、絶対に肉付けしてはいけない。
        4. ツールが出力した文字列のみを返すこと。
        """,
        expected_output="ツールから返却された文字列そのもの（1文字も変更禁止）",
        agent=manager
    )

    crew = Crew(
        agents=[manager],
        tasks=[task],
        process=Process.sequential
    )

    return crew.kickoff()