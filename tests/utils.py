import httpx


def is_responsive(url):
    try:
        response: httpx.Response = httpx.get(url)
        response.raise_for_status()
    except httpx.RequestError:
        return False
    except httpx.HTTPStatusError:
        return False
    return True
