import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Content-Type": "application/json",
}
resp = requests.get(
    url="https://thevirustracker.com/free-api?countryTimeline=US", headers=headers
)

print(resp)
