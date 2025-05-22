import requests
import json
response = requests.get(
  url="https://openrouter.ai/api/v1/auth/key",
  headers={
    "Authorization": f"Bearer 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"
  }
)
print(json.dumps(response.json(), indent=2))


