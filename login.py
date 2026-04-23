"""Login script for ews.mtyl0.com.

Responsibilities:
- Fetch captcha state/image
- Perform GraphQL Login mutation
- Persist token, user_info, udid to local files
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import pathlib
import uuid
from typing import Any, Dict, Optional

import requests


BASE_URL = "https://ews.mtyl0.com"
GRAPHQL_URL = f"{BASE_URL}/APIV2/GraphQL"
DEFAULT_APP_KEY = "acZCW1FPBjNV"
DEFAULT_UDID = "b9bb9c21-f51d-45bd-85e5-27d99c8a2b42"

CAPTCHA_QUERY = """
{
  CaptchaData {
    captcha_id
    captcha_base64_string
    need_verify
    __typename
  }
}
"""

LOGIN_MUTATION = """
mutation Login(
  $app_key: String!,
  $account: String!,
  $password: String!,
  $captcha_id: String,
  $captcha_code: String,
  $google_code: String,
  $bank_card_real_name: String,
  $two_step_token: String
) {
  info: Login(
    app_key: $app_key,
    account: $account,
    password: $password,
    captcha_id: $captcha_id,
    captcha_code: $captcha_code,
    google_code: $google_code,
    bank_card_real_name: $bank_card_real_name,
    two_step_token: $two_step_token
  ) {
    user_id
    token
    user_info {
      id
      user_account
      user_email
      user_name
      user_avatar
      user_nickname
      is_beta
      mobile_number
      is_bind_google_code
      is_set_hand_lock
      hand_lock_active
      has_bind_bank_card
      is_proxy
      has_set_balance_password
      has_bound_telegram
      create_time
      recharge_has_bind_bank_card
      user_setting {
        index_guide
        __typename
      }
      first_bank_card
      user_red_line
      proxy_level
      user_safe_question_info {
        is_setting_completed
        __typename
      }
      user_safe_question {
        question_id
        __typename
      }
      financial {
        has_bind_cryptocurrency_non_cny
        __typename
      }
      dual_mode
      __typename
    }
  }
}
"""


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
            ),
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": BASE_URL,
            "referer": f"{BASE_URL}/user/login-form/login",
        }
    )
    return session


def graphql_request(
    session: requests.Session,
    payload: Dict[str, Any],
    udid: str,
) -> Dict[str, Any]:
    response = session.post(
        GRAPHQL_URL,
        params={"l": "zh-cn", "pf": "web", "udid": udid},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data


def fetch_captcha(session: requests.Session, udid: str) -> Dict[str, Any]:
    data = graphql_request(
        session,
        {
            "query": CAPTCHA_QUERY,
            "variables": {},
            "operationName": None,
        },
        udid,
    )
    return data["data"]["CaptchaData"]


def save_captcha_image(
    captcha_data: Dict[str, Any], output_path: pathlib.Path
) -> Optional[pathlib.Path]:
    image_b64 = captcha_data.get("captcha_base64_string")
    if not image_b64:
        return None
    output_path.write_bytes(base64.b64decode(image_b64))
    return output_path


def login(
    session: requests.Session,
    udid: str,
    captcha_id: Optional[str],
    captcha_code: str,
    app_key: str,
    account: str,
    password: str,
) -> Dict[str, Any]:
    payload = {
        "operationName": "Login",
        "variables": {
            "app_key": app_key,
            "account": account,
            "password": password,
            "captcha_id": captcha_id,
            "captcha_code": captcha_code,
            "google_code": "",
            "bank_card_real_name": None,
            "two_step_token": None,
        },
        "query": LOGIN_MUTATION,
    }
    data = graphql_request(session, payload, udid)
    return data["data"]["info"]


def persist_session(token: str, user_info: Dict[str, Any], udid: str) -> None:
    pathlib.Path("session_token.txt").write_text(token.strip(), encoding="utf-8")
    pathlib.Path("user_info.json").write_text(
        json.dumps(user_info, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    pathlib.Path("udid.txt").write_text(udid.strip(), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login to ews.mtyl0.com via GraphQL")
    parser.add_argument("--account", help="Login account")
    parser.add_argument("--password", help="Login password")
    parser.add_argument("--app-key", default=DEFAULT_APP_KEY, help="GraphQL app_key")
    parser.add_argument(
        "--udid", default=DEFAULT_UDID, help="Device UDID used by the site"
    )
    parser.add_argument(
        "--captcha-file", default="captcha.png", help="Where to save captcha image"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = build_session()

    account = args.account or input("account: ").strip()
    password = args.password or getpass.getpass("password: ")
    udid = args.udid or str(uuid.uuid4())

    if not account:
        raise SystemExit("account is required")
    if not password:
        raise SystemExit("password is required")

    captcha_data = fetch_captcha(session, udid)
    print("captcha_data:")
    print(json.dumps(captcha_data, ensure_ascii=False, indent=2))

    captcha_file = save_captcha_image(captcha_data, pathlib.Path(args.captcha_file))
    if captcha_file:
        print(f"captcha image saved to: {captcha_file}")

    captcha_code = ""
    if captcha_data.get("need_verify"):
        captcha_code = input("captcha_code: ").strip()

    login_result = login(
        session=session,
        udid=udid,
        captcha_id=captcha_data.get("captcha_id"),
        captcha_code=captcha_code,
        app_key=args.app_key,
        account=account,
        password=password,
    )

    token = login_result.get("token")
    if not token:
        raise RuntimeError("Login succeeded but token is missing in response")

    user_info = login_result.get("user_info") or {}
    persist_session(token=token, user_info=user_info, udid=udid)

    print("login succeeded")
    print("token saved to session_token.txt")
    print("udid saved to udid.txt")
    print("user info saved to user_info.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
