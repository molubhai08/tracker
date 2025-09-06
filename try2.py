import requests

url = "https://fd69c9bba687.ngrok-free.app/response"
data = {"query": "Show my daily water intake for 28 aug 2025"}

response = requests.post(url, json=data)
print(response.json())
