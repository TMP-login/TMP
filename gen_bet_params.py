
"""Generate lottery bet parameters interactively and save to JSON file."""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any, Dict, List

# bet_mode 选项映射
BET_MODE_OPTIONS = {
    "1": ("TwoYuan", "2元"),
    "2": ("TwoJiao", "2角"),
    "3": ("TwoFen", "2分"),
    "4": ("TwoLi", "2厘"),
    "5": ("OneYuan", "1元"),
    "6": ("OneJiao", "1角"),
    "7": ("OneFen", "1分"),
    "8": ("OneLi", "1厘"),
}


def get_position_numbers(position: int) -> List[str]:
    """交互式获取某个位置选择的数字（0-9）。"""
    while True:
        inp = input(
            f"第{position}位 选择的数字（可输入任意字符，系统会提取其中的 0-9，留空跳过）: "
        ).strip()
        if not inp:
            return []

        nums = sorted(set(re.findall(r"[0-9]", inp)))

        if not nums:
            print("  ❌ 没有提取到任何数字，请至少输入 0-9 中的一个数字")
            continue
        if len(nums) > 9:
            print("  ❌ 每位最多选择 9 个数字")
            continue

        print(f"  ✓ 已选择（去重并排序后）: {', '.join(nums)}")
        return nums


def get_bet_mode() -> str:
    """交互式选择单注金额。"""
    print("\n选择单注金额:")
    for key, (mode, desc) in BET_MODE_OPTIONS.items():
        print(f"  {key}: {desc:6} ({mode})")

    while True:
        choice = input("请选择 (1-8): ").strip()
        if choice in BET_MODE_OPTIONS:
            mode, desc = BET_MODE_OPTIONS[choice]
            print(f"  ✓ 已选择: {desc}")
            return mode
        print("  ❌ 选择有误，请输入 1-8")


def get_bet_multiple() -> int:
    """交互式输入倍数。"""
    while True:
        try:
            inp = input("\n输入倍数（如 1, 23, 100）: ").strip()
            m = int(inp)
            if m > 0:
                print(f"  ✓ 已输入: {m}倍")
                return m
            print("  ❌ 倍数必须大于 0")
        except ValueError:
            print("  ❌ 请输入有效的整数")


def build_bet_info(positions: List[List[str]]) -> str:
    """构建 bet_info 字符串（JSON 格式）。"""
    return json.dumps(positions, ensure_ascii=False)


def show_summary(params: Dict[str, Any]) -> None:
    """打印下注参数摘要。"""
    print("\n" + "=" * 60)
    print("下注参数摘要")
    print("=" * 60)

    # 解析 bet_info
    bet_info_data = json.loads(params["bet_info"])
    print(f"5个位置选择:")
    for i, nums in enumerate(bet_info_data, 1):
        if nums:
            print(f"  第{i}位: {', '.join(nums)}")
        else:
            print(f"  第{i}位: (未选择)")

    print(f"\n单注金额: {params['bet_mode']}")
    print(f"倍数: {params['bet_multiple']}")
    print(f"总参数数: {len(json.dumps(params))}")
    print("=" * 60)


def main() -> int:
    print("\n" + "=" * 60)
    print("彩票下注参数生成工具")
    print("=" * 60)

    # 获取 5 个位置的数字
    print("\n请为 5 个位置选择数字（0-9）:")
    positions: List[List[str]] = []
    for i in range(1, 6):
        nums = get_position_numbers(i)
        positions.append(nums)

    # 获取 bet_mode 和 bet_multiple
    bet_mode = get_bet_mode()
    bet_multiple = get_bet_multiple()

    # 生成 bet_info
    bet_info = build_bet_info(positions)

    # 构建完整的下注参数
    bet_params: Dict[str, Any] = {
        "game_id": 370,
        "game_type_id": 65,
        "bet_info": bet_info,
        "bet_mode": bet_mode,
        "bet_multiple": bet_multiple,
        "bet_percent_type": "AdjustPercentType",
        "bet_percent": 0,
        "is_follow": False,
        "follow_commission_percent": None,
    }

    # 显示摘要
    show_summary(bet_params)

    # 保存为 JSON 文件
    output_file = pathlib.Path("bet_params.json")
    output_file.write_text(
        json.dumps(bet_params, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n✓ 参数已保存到: {output_file}")
    print(f"\n你可以在 bet.py 中使用这个文件，或通过以下方式查看:")
    print(f"  python -m json.tool {output_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
