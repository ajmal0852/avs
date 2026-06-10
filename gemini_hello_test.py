from __future__ import annotations

import traceback
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values
from google import genai
from google.genai import types


MODEL_NAME = "gemini-2.5-flash"


def load_api_key() -> str:
    values = dotenv_values(Path(__file__).resolve().with_name(".env"))
    api_key = (values.get("GOOGLE_API_KEY") or values.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("No Gemini API key found in .env")
    return api_key


def mask_key(api_key: str) -> str:
    if len(api_key) < 10:
        return "<too-short-to-mask>"
    return f"{api_key[:6]}...{api_key[-4:]}"


def install_request_logging(client: genai.Client) -> None:
    api_client = getattr(client, "_api_client", None)
    httpx_client = getattr(api_client, "_httpx_client", None)
    if httpx_client is None:
        return

    original_send = getattr(httpx_client, "send", None)
    if original_send is None or getattr(original_send, "__wrapped_by_hackathon2__", False):
        return

    def logged_send(request, *args, **kwargs):
        request_url = str(getattr(request, "url", ""))
        parsed_url = urlparse(request_url)
        print(
            f"REQUEST_LOG method={getattr(request, 'method', '<unknown>')} hostname={parsed_url.hostname} url={request_url} path={parsed_url.path}"
        )
        return original_send(request, *args, **kwargs)

    logged_send.__wrapped_by_hackathon2__ = True  # type: ignore[attr-defined]
    httpx_client.send = logged_send  # type: ignore[assignment]


def main() -> None:
    api_key = load_api_key()
    print(f"API_KEY_LEN={len(api_key)}")
    print(f"API_KEY_PREVIEW={mask_key(api_key)}")
    print(f"STARTS_WITH_AIZA={api_key.startswith('AIza')}")

    client = genai.Client(api_key=api_key)
    install_request_logging(client)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="hello",
            config=types.GenerateContentConfig(temperature=0),
        )
        print("RESPONSE_TEXT=")
        print(response.text)
        print("RESPONSE_REPR=")
        print(repr(response))
    except Exception as exc:
        print("REQUEST_ENDPOINT=")
        print(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent")
        print("REQUEST_METHOD=POST")
        print("REQUEST_BODY=contents='hello', temperature=0")
        print("EXCEPTION=")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()