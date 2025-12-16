from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# AIに対して入力の型を指定する
class QueryInput(BaseModel):
    query: str = Field(description="ユーザーからの依頼内容や質問文の文字列そのもの。JSON形式やメタデータを含めず、テキストの値だけを渡してください。")


# --- 既存の要件定義エージェント (外部Functions想定) ---
class RequirementBotConnector(BaseTool):
    name: str = "RequirementDefinitionBot"
    description: str = "要件定義に関する質問や、ドキュメント作成の依頼は、必ずこのツールを使用してください。引数'query'には、ユーザーの依頼文(文字列)をそのまま渡してください。"
    args_schema: type[BaseModel] = QueryInput

    # 【現在のダミー実装】
    def _run(self, query: str) -> str:
        print(f"[Connector] 要件定義ボットに接続中... 入力: {query}")
        return f"【要件定義エージェントからの回答】:「{query}」についての要件定義ドラフトを作成しました。（接続テスト成功）"


# --- 脱線検知エージェント (将来の想定) ---
class DeviationCheckConnector(BaseTool):
    name: str = "DeviationCheckBot"
    description: str = "会議のアジェンダからの脱線チェックや、進捗確認は、このツールを使用してください。引数'query'には、ユーザーの依頼文(文字列)をそのまま渡してください。"
    args_schema: type[BaseModel] = QueryInput

    # 【現在のダミー実装】
    def _run(self, query: str) -> str:
        print(f"[Connector] 脱線検知係(LangGraph)に接続中... 入力: {query}")
        return f"【脱線検知エージェントからの回答】:「{query}」に基づき、脱線確認についてのまとめを作成しました。（接続テスト成功）"


# ---
# 開発工数・費用見積もりエージェント (将来の想定) ---
class CostEstimationConnector(BaseTool):
    name: str = "CostEstimationBot"
    description: str = "システム開発の工数見積もりに関しては、このツールを使用してください。引数'query'には、ユーザーの依頼文(文字列)をそのまま渡してください。"
    args_schema: type[BaseModel] = QueryInput

    # 【現在のダミー実装】
    def _run(self, query: str) -> str:
        print(f"[Connector] 開発見積もりボットに接続中... 入力: {query}")
        return f"【開発工数見積もりエージェントからの回答】:「{query}」に基づき、開発工数と費用の概算を作成しました。（接続テスト成功）"
