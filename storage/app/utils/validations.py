from starlette.datastructures import Headers

from config import AppConfig


def get_token(headers: Headers) -> str | None:
    print("HEADERS:", dict(headers), flush=True)
    method, data = headers.get("Authorization", "NO None").split(maxsplit=1)
    if method == "OAuth":
        return data
    return None


def check_admin_auth(headers: Headers) -> bool:
    method, data = headers.get("Authorization", "NO None").split(maxsplit=1)
    if method == "OAuth":
        return data == AppConfig.ADMIN_TOKEN
    return False
