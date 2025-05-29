import requests

response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
    headers={
        "authorization": f"Bearer sk-1wYOr8q590t3qgwN2cRqtXaiuNnETWuiFAiz9Tb8rr7UElbc",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "a man with a cat",
        "output_format": "webp",
    },
)

if response.status_code == 200:
    with open("./cat2.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))

print(response.status_code)