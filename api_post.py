# general imports
import requests

# custom imports


def post_order(url, api_key, payload):
    """Post the order to the API endpoint."""

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()  # raises HTTPError for 4xx / 5xx
        data = response.json()  # only reached on success

        return True

    except requests.Timeout:
        print("Server did not respond in time; safe to retry.")
        return False
    except requests.HTTPError as e:
        print(f"Server returned an error: {e}")
        return False
    except requests.JSONDecodeError:
        print(f"Response was not JSON: {response.text[:200]!r}")
        return False
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # timeouts, no network, bad URL
        return False
