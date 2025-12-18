from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from requirements_processor import RequirementsTargetIdentifier

# AIに渡す入力の型
class QueryInput(BaseModel):
    query: str = Field(description="ユーザーからの依頼内容や質問文の文字列")

# 要件定義書解析・更新対象特定エージェント
class RequirementsProcessorConnector(BaseTool):
    name: str = "RequirementsProcessorBot"
    description: str = (
        "要件定義書の解析・更新対象特定を行います。"
        "引数 'query' には、ユーザー依頼文をそのまま渡してください。"
    )
    args_schema: type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        # RequirementsTargetIdentifier を使って解析・処理
        processor = RequirementsTargetIdentifier()
        result = processor.process(query)
        return result
