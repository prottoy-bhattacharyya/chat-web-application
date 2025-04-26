import requests
import json
response = requests.get(
  url="https://openrouter.ai/api/v1/auth/key",
  headers={
    "Authorization": f"Bearer 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"
  }
)
print(json.dumps(response.json(), indent=2))
