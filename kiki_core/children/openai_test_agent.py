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
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            body = res.read().decode("utf-8")
            return body

    except Exception as e:
        return f"[openai-test 呼び出し失敗] {e}"
