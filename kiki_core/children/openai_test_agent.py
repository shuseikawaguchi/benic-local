import json
import urllib.request


OPENAI_TEST_URL = "https://kiki-dev-func-01.azurewebsites.net/api/openai-test"


def run_openai_test(query: str) -> str:
    payload = {
        "query": query
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        OPENAI_TEST_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "kiki-openai-test/1.0",
        },
        method="POST"
    )
# Azure App Service / Functions 環境では、urllib の POST に "User-Agent" が無いと
# レスポンス読み取りが timeout することがある。
# curl では再現せず、Python クライアントのみ失敗したため明示的に指定。

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            body = res.read().decode("utf-8")
            return f"<RESULT>{body}</RESULT>"

    except Exception as e:
        return f"[openai-test 呼び出し失敗] {e}"
