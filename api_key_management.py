# import requests
# import json

# PROVISIONING_API_KEY = "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"
# BASE_URL = "https://openrouter.ai/api/v1/keys"
# response = requests.post(
#     f"{BASE_URL}/",
#     headers={
#         "Authorization": f"Bearer {PROVISIONING_API_KEY}",
#         "Content-Type": "application/json"
#     },
#     json={
#         "name": "AI-chat-app-key",
#         "label": "Prottoy",
#         "limit": 1000  # Optional credit limit
#     }
# )

# print(response)

import requests
import json

PROVISIONING_API_KEY = "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"  # Replace with your actual provisioning API key
BASE_URL = "https://openrouter.ai/api/v1/keys"

def create_openrouter_api_key(name, label, limit=None):
    """
    Creates a new API key on OpenRouter using the provisioning API key.

    Args:
        name (str): The name for the new API key.
        label (str): The label for the new API key.
        limit (int, optional): An optional credit limit for the new key. Defaults to None.

    Returns:
        str: The hash (API key) of the newly created key, or None on error.
    """
    headers = {
        "Authorization": f"Bearer {PROVISIONING_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": name,
        "label": label,
    }
    if limit is not None:
        payload["limit"] = limit  # Add limit to the payload if provided

    try:
        response = requests.post(f"{BASE_URL}/", headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()  # Parse the JSON response

        if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            new_key_hash = data["data"][0].get("hash")  # Safely get the 'hash'
            if new_key_hash:
                return new_key_hash
            else:
                print("Error: 'hash' not found in the response data.")
                return None
        else:
            print("Error: Unexpected response structure from OpenRouter API.")
            print(f"Response: {data}") # print the response
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error creating API key: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

# Example usage:
new_key = create_openrouter_api_key(
    name="My Application Key",
    label="app-123",
    limit=500  # Optional credit limit
)

if new_key:
    print(f"Successfully created API key.  The key hash is: {new_key}")
    #  IMPORTANT:  Store this key securely.  You'll use this 'new_key' (the hash)
    #  to make requests to the OpenRouter API.
else:
    print("Failed to create API key.")
