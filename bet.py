"""Bet script for ews.mtyl0.com.

Responsibilities:
- Read token/udid from local txt files
- Optionally query current lottery cycle
- Submit AddLotteryOrders mutation
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, Optional

import requests


BASE_URL = "https://ews.mtyl0.com"
GRAPHQL_URL = f"{BASE_URL}/APIV2/GraphQL"

GET_LOTTERY_CYCLE_QUERY = """
query GetLotteryCycle($game_id: Int!, $row_count: Int) {
  LotteryGame(game_id: $game_id) {
    game_id
    game_value
    base_game
    official_website
    lottery_cycle_now {
      now_cycle_id
      now_cycle_value
      now_cycle_count_down
      now_cycle_cool_down
      last_cycle_value
      last_cycle_game_result
      future_cycle_list {
        cycle_id
        cycle_value
        __typename
      }
      beforehand_draw {
        suffix
        hash
        __typename
      }
      __typename
    }
    lottery_result_history(row_count: $row_count) {
      cycle_value
      game_result
      open_time
      extra_context {
        hash
        block
        __typename
      }
      beforehand_draw {
        complete
        suffix
        hash
        __typename
      }
      __typename
    }
    extra_info {
      trxbh_account_from
      trxbh_account_to
      trxbh_URL
      __typename
    }
    __typename
  }
}
"""

ADD_LOTTERY_ORDERS_MUTATION = """
mutation AddLotteryOrders($input: [AddLotteryOrderInputObj]!) {
  AddLotteryOrders(orders: $input) {
    message
    order_ids
    __typename
  }
}
"""


def read_text(path: pathlib.Path, name: str) -> str:
    if not path.exists():
        raise SystemExit(f"{name} file not found: {path}")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise SystemExit(f"{name} file is empty: {path}")
    return value


def resolve_account(cli_account: Optional[str], user_info_file: pathlib.Path) -> str:
    if cli_account:
        return cli_account.strip()
    if not user_info_file.exists():
        raise SystemExit(
            "account is required: pass --account or ensure user_info.json exists"
        )
    try:
        data = json.loads(user_info_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid user_info json: {user_info_file}: {exc}") from exc
    account = str(data.get("user_account") or "").strip()
    if not account:
        raise SystemExit(
            "account not found in user_info.json: pass --account explicitly"
        )
    return account


def load_json_file(path: pathlib.Path, name: str) -> Dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"{name} file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {name} json: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{name} must be a JSON object: {path}")
    return data


def resolve_param(cli_value: Any, json_value: Any, default: Any = None) -> Any:
    if cli_value is not None:
        return cli_value
    if json_value is not None:
        return json_value
    return default


def build_session(token: str, game_id: int) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "authorization": token,
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
            ),
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": BASE_URL,
            "referer": f"{BASE_URL}/lottery/{game_id}",
        }
    )
    return session


def graphql_request(
    session: requests.Session,
    payload: Dict[str, Any],
    udid: str,
    account: str,
) -> Dict[str, Any]:
    response = session.post(
        GRAPHQL_URL,
        params={"l": "zh-cn", "pf": "web", "udid": udid, "ac": account},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data


def get_current_cycle(
    session: requests.Session,
    udid: str,
    account: str,
    game_id: int,
    row_count: int = 30,
) -> Dict[str, Any]:
    payload = {
        "operationName": "GetLotteryCycle",
        "variables": {"game_id": game_id, "row_count": row_count},
        "query": GET_LOTTERY_CYCLE_QUERY,
    }
    data = graphql_request(session, payload, udid, account)
    lottery_game = data["data"]["LotteryGame"]
    return lottery_game["lottery_cycle_now"]


def add_lottery_orders(
    session: requests.Session,
    udid: str,
    account: str,
    game_id: int,
    game_type_id: int,
    game_cycle_id: int,
    bet_info: str,
    bet_mode: str,
    bet_multiple: int,
    bet_percent_type: str,
    bet_percent: int,
    is_follow: bool,
    follow_commission_percent: Optional[float],
) -> Dict[str, Any]:
    payload = {
        "operationName": "AddLotteryOrders",
        "variables": {
            "input": [
                {
                    "game_id": game_id,
                    "game_type_id": game_type_id,
                    "game_cycle_id": game_cycle_id,
                    "bet_info": bet_info,
                    "bet_mode": bet_mode,
                    "bet_multiple": bet_multiple,
                    "bet_percent_type": bet_percent_type,
                    "bet_percent": bet_percent,
                    "is_follow": is_follow,
                    "follow_commission_percent": follow_commission_percent,
                }
            ]
        },
        "query": ADD_LOTTERY_ORDERS_MUTATION,
    }
    data = graphql_request(session, payload, udid, account)
    return data["data"]["AddLotteryOrders"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit lottery order with saved token")
    parser.add_argument("--account", help="Account used in query param ac")
    parser.add_argument("--token-file", default="session_token.txt", help="Token txt file")
    parser.add_argument("--udid-file", default="udid.txt", help="UDID txt file")
    parser.add_argument(
        "--user-info-file",
        default="user_info.json",
        help="Fallback file to read user_account when --account is omitted",
    )
    parser.add_argument(
        "--bet-param-file",
        default="bet_params.json",
        help="JSON file containing default bet parameters",
    )

    parser.add_argument("--game-id", type=int, help="Lottery game_id")
    parser.add_argument("--game-type-id", type=int, help="Lottery game_type_id")
    parser.add_argument("--game-cycle-id", type=int, help="Current game cycle id")
    parser.add_argument("--row-count", type=int, default=30, help="History row_count for cycle query")

    parser.add_argument(
        "--bet-info",
        help="bet_info JSON-string required by API",
    )
    parser.add_argument("--bet-mode", help="bet_mode")
    parser.add_argument("--bet-multiple", type=int, help="bet_multiple")
    parser.add_argument("--bet-percent-type", help="bet_percent_type")
    parser.add_argument("--bet-percent", type=int, help="bet_percent")
    parser.add_argument("--is-follow", action="store_true", help="is_follow")
    parser.add_argument("--follow-commission-percent", type=float, help="follow_commission_percent")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    token = read_text(pathlib.Path(args.token_file), "token")
    udid = read_text(pathlib.Path(args.udid_file), "udid")
    account = resolve_account(args.account, pathlib.Path(args.user_info_file))
    bet_defaults = load_json_file(pathlib.Path(args.bet_param_file), "bet parameter")

    game_id = resolve_param(args.game_id, bet_defaults.get("game_id"), 370)
    game_type_id = resolve_param(args.game_type_id, bet_defaults.get("game_type_id"), 65)
    bet_info = resolve_param(args.bet_info, bet_defaults.get("bet_info"))
    bet_mode = resolve_param(args.bet_mode, bet_defaults.get("bet_mode"))
    bet_multiple = resolve_param(args.bet_multiple, bet_defaults.get("bet_multiple"), 1)
    bet_percent_type = resolve_param(
        args.bet_percent_type, bet_defaults.get("bet_percent_type"), "AdjustPercentType"
    )
    bet_percent = resolve_param(args.bet_percent, bet_defaults.get("bet_percent"), 0)
    follow_commission_percent = resolve_param(
        args.follow_commission_percent,
        bet_defaults.get("follow_commission_percent"),
        None,
    )
    is_follow = bool(bet_defaults.get("is_follow", False))
    if args.is_follow:
        is_follow = True

    if bet_info is None:
        raise SystemExit(
            "bet_info is required: provide it in bet_params.json or pass --bet-info"
        )
    if bet_mode is None:
        raise SystemExit(
            "bet_mode is required: provide it in bet_params.json or pass --bet-mode"
        )

    session = build_session(token=token, game_id=game_id)

    cycle_id = args.game_cycle_id
    if cycle_id is None:
        cycle = get_current_cycle(
            session=session,
            udid=udid,
            account=account,
            game_id=game_id,
            row_count=args.row_count,
        )
        cycle_id = int(cycle["now_cycle_id"])
        print("queried current cycle:")
        print(json.dumps(cycle, ensure_ascii=False, indent=2))

    order_result = add_lottery_orders(
        session=session,
        udid=udid,
        account=account,
        game_id=game_id,
        game_type_id=game_type_id,
        game_cycle_id=cycle_id,
        bet_info=bet_info,
        bet_mode=bet_mode,
        bet_multiple=bet_multiple,
        bet_percent_type=bet_percent_type,
        bet_percent=bet_percent,
        is_follow=is_follow,
        follow_commission_percent=follow_commission_percent,
    )

    print("order result:")
    print(json.dumps(order_result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
