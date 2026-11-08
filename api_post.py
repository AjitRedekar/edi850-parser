# general imports
import requests

# custom imports


def post_order(payload):
    """Post the order to the API endpoint."""

    try:
        response = requests.post(
            "https://httpbin.org/post",
            json=payload,
            timeout=20,
        )

        response.raise_for_status()  # raises HTTPError for 4xx / 5xx
        data = response.json()  # only reached on success
        print(data["json"]["po_number"])

    except requests.Timeout:
        print("Server did not respond in time; safe to retry.")
    except requests.HTTPError as e:
        print(f"Server returned an error: {e}")
    except requests.JSONDecodeError:
        print(f"Response was not JSON: {response.text[:200]!r}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # timeouts, no network, bad URL


# if __name__ == "__main__":
#     try:
#         pi_order = sys.argv[1]

#     except IndexError:
#         print("order missing as input to post API")

#     post_order(pi_order)
