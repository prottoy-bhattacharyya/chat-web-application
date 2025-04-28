import requests
import json
response = requests.get(
  url="https://openrouter.ai/api/v1/auth/key",
  headers={
    "Authorization": f"Bearer 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"
  }
)
print(json.dumps(response.json(), indent=2))


