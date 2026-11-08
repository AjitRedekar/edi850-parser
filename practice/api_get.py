import requests

try:
    response = requests.get(
        "https://httpbin.org/delay/28",
        params={"PO": "4500123456"},
        timeout=10,
    )

    response.raise_for_status()  # raises HTTPError for 4xx / 5xx
    data = response.json()  # only reached on success
    print(data["args"])

except requests.Timeout:
    print("Server did not respond in time; safe to retry.")
except requests.JSONDecodeError:
    print(f"Response was not JSON: {response.text[:200]!r}")
except requests.RequestException as e:
    print(f"Request failed: {e}")  # timeouts, no network, bad URL
except requests.HTTPError as e:
    print(f"Server returned an error: {e}")
