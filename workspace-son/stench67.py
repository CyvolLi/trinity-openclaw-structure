#!/usr/bin/env python3
"""
数字恶臭化工具 v67 — 用67系列数字组合目标数字
============================================
基于网络迷因「67恶臭梗」，通过 6、7、67、6767、6776 等
数字组合加减乘除来匹配任意目标数字。

用法:
    python3 stench67.py <目标数字>
    python3 stench67.py 114514
"""

import sys
import itertools
import random
from typing import List, Tuple, Optional

# ============ 恶臭数字池（67系）============
STENCH_NUMBERS = [
    # 基础数字
    6, 7,
    # 两位数
    67, 76,
    # 三位数
    676, 767, 667, 677, 766, 776,
     # 四位数
     6767, 6776, 6677, 7667, 7766, 7676,
      # 更好玩的五位数
      67676, 67667, 67767, 67776, 66767, 66776, 76676, 76767,
      # 六位数（恶臭全开）
      676767, 677676, 667767, 767676,
]

# 操作符符号
OPERATORS = ['+', '-', '*', '/']

# 恶臭梗注释模板
STENCH_COMMENTS = [
    "🤢 太臭了！",
    "💩 恶臭数字！",
    "🐷 你这数字不对劲",
    "🤮 呕——",
    "🔥 纯正67味",
    "👴 有内味了",
    "😤 数字恶臭化完成",
    "🎯 精准命中！",
    "💯 纯度极高",
    "🤯 大脑在颤抖",
    "🥴 67,67,67!",
    "⚡ 六七十级恶臭",
    "💀 数字已经臭不可闻",
    "👃 闻到味了吗",
    "🔥 🔥 🔥",
]

def format_stench(num: int) -> str:
    """返回某个恶臭数字的梗风格表示"""
    num_map = {
        6: "六",
        7: "七",
        67: "六十七",
        76: "七十六",
        676: "六七六",
        767: "七六七",
        667: "六六七",
        677: "六七七",
        766: "七六六",
        776: "七七六",
        6767: "六七六七",
        6776: "六七七六",
        6677: "六六七七",
        7667: "七六六七",
        7766: "七七六六",
        7676: "七六七六",
        67676: "六七六七六",
        67667: "六七六六七",
        67767: "六七七六七",
        67776: "六七七七六",
        66767: "六六七六七",
        66776: "六六七七六",
        76676: "七六六七六",
        76767: "七六七六七",
        676767: "六七六七六七",
        677676: "六七七六七六",
        667767: "六六七七六七",
        767676: "七六七六七六",
    }
    return num_map.get(num, str(num))


# ============ 算法一：暴力双数组合 ============

def find_two_number_expressions(target: int) -> List[str]:
    """
    用两个恶臭数字的简单运算匹配目标。
    输出格式：6 + 67 = 73 之类的。
    """
    results = []
    for a in STENCH_NUMBERS:
        for b in STENCH_NUMBERS:
            for op in OPERATORS:
                try:
                    if op == '+':
                        val = a + b
                    elif op == '-':
                        val = a - b
                    elif op == '*':
                        val = a * b
                    elif op == '/':
                        if b == 0:
                            continue
                        # 只接受整除结果
                        if a % b != 0:
                            continue
                        val = a // b

                    if val == target:
                        expr = f"{a} {op} {b} = {target}"
                        comment = random.choice(STENCH_COMMENTS)
                        results.append(f"{expr}    {comment}")
                except:
                    continue
    return results


# ============ 算法二：多步表达式 ============

def _dfs_multi_expr(numbers_used: List[int], current_val: int,
                    target: int, depth: int, max_depth: int,
                    expr_str: str, results: set) -> None:
    """
    DFS 递归构建多步恶臭表达式。
    每步从 STENCH_NUMBERS 中选一个数，与当前结果运算。
    """
    if depth > max_depth:
        return
    if current_val == target and depth > 1:
        results.add(f"{expr_str} = {target}    🤢 恶臭达成！")
        return
    if depth == max_depth:
        return

    # 剪枝：如果 current_val 已经远超出范围（对非除法场景）
    limit = max(abs(target) * 10, 1000000)
    if abs(current_val) > limit:
        return

    for n in STENCH_NUMBERS:
        # 加法
        _dfs_multi_expr(
            numbers_used + [n], current_val + n,
            target, depth + 1, max_depth,
            f"({expr_str} + {n})", results
        )
        # 减法
        _dfs_multi_expr(
            numbers_used + [n], current_val - n,
            target, depth + 1, max_depth,
            f"({expr_str} - {n})", results
        )
        # 乘法
        _dfs_multi_expr(
            numbers_used + [n], current_val * n,
            target, depth + 1, max_depth,
            f"({expr_str} × {n})", results
        )
        # 除法（排除除不尽的情况）
        if n != 0 and current_val % n == 0:
            _dfs_multi_expr(
                numbers_used + [n], current_val // n,
                target, depth + 1, max_depth,
                f"({expr_str} ÷ {n})", results
            )


def find_multi_expressions(target: int, max_depth: int = 3) -> List[str]:
    """
    寻找多步恶臭表达式。
    从每个恶臭数字开始，逐步运算。
    """
    results = set()
    for start in STENCH_NUMBERS:
        _dfs_multi_expr([start], start, target, 1, max_depth, str(start), results)
    return list(results)


# ============ 算法三：拆解式 ============

def find_decomposition_expressions(target: int) -> List[str]:
    """
    将目标拆解成 67x + 6y + 7z 的形式。
    例如：目标 = 67*a + 6*b + 7*c
    """
    results = []
    # 用 67、6、7 的线性组合
    for a in range(-20, 21):
        remaining_after_67 = target - 67 * a
        for b in range(-50, 51):
            remaining = remaining_after_67 - 6 * b
            for c in range(-50, 51):
                if 7 * c == remaining:
                    parts = []
                    comment_parts = []
                    if a != 0:
                        parts.append(f"67×{a}")
                        comment_parts.append(f"{abs(a)}个67")
                    if b != 0:
                        parts.append(f"{'+' if b > 0 else '-'} 6×{abs(b)}" if parts else f"6×{b}")
                        if b > 0:
                            comment_parts.append(f"{b}个6")
                        else:
                            comment_parts.append(f"减去{abs(b)}个6")
                    if c != 0:
                        sign = '+' if (a != 0 or b != 0) and c > 0 else ('-' if c < 0 else '')
                        parts.append(f"{sign} 7×{abs(c)}" if parts else f"7×{c}")
                        if c > 0:
                            comment_parts.append(f"{c}个7")
                        else:
                            comment_parts.append(f"减去{abs(c)}个7")

                    if len(parts) >= 1:
                        expr = " ".join(parts).replace("+ -", "- ")
                        decomposition = " + ".join(comment_parts).replace(" + -", " - ").replace("+ -", "- ").replace("+ 减去", "减去")
                        results.append(
                            f"{target} = {expr}    🐷 即 {decomposition}，纯度极高！"
                        )
                    break  # inner loop
                if 7 * c > remaining:
                    break
        # limit results
        if len(results) > 10:
            break
    return results


# ============ 算法四：67 进制(趣味版) ============

def find_67base_expression(target: int) -> Optional[str]:
    """
    用 67 进制思想：把目标转成 67 进制，每一位用 67 的幂表示。
    """
    if target == 0:
        return None

    # 转为 67 进制
    digits = []
    n = abs(target)
    while n > 0:
        digits.append(n % 67)
        n //= 67

    # 构建表达式
    parts = []
    sign = '-' if target < 0 else ''
    for i, d in enumerate(digits):
        if d == 0:
            continue
        if i == 0:
            if d == 1:
                parts.append("1")
            else:
                parts.append(f"{d}")
        elif i == 1:
            suffix = f"×67" if d == 1 else f"×67×{d}" if d != 1 else "×67"
            # actually: d * 67^i
            if d != 1:
                parts.append(f"67×{d}")
            else:
                parts.append("67")
        else:
            if d != 1:
                parts.append(f"67^{i}×{d}")
            else:
                parts.append(f"67^{i}")

    if not parts:
        return None

    expr = " + ".join(reversed(parts)).replace("67×", "67×")
    return f"{target} = {sign}{expr}    🧮 67进制展开，纯度惊人！"


# ============ 主输出函数 ============

def stench_number(target: int, max_results: int = 20) -> None:
    """对目标数字执行恶臭化，打印结果。"""
    if not isinstance(target, int) or target == 0:
        print("❌ 请输入一个非零整数")
        return

    print(f"\n{'='*60}")
    print(f"  🦨 数字恶臭化工具 v67")
    print(f"{'='*60}")
    print(f"\n  目标数字：\033[1;33m{target}\033[0m")
    print(f"  开始恶臭化...\n")

    all_results = []

    # ======== 方法一：双数组合 ========
    pair_results = find_two_number_expressions(target)
    if pair_results:
        all_results.append(("🔢 双数组合（双臭合璧）", pair_results[:8]))

    # ======== 方法二：67分解 ========
    decom_results = find_decomposition_expressions(target)
    if decom_results:
        all_results.append(("🧩 67分解（条理清晰）", decom_results[:6]))

    # ======== 方法三：多步表达式（浅搜索） ========
    multi_results = find_multi_expressions(target, max_depth=3)
    # 过滤掉太长的
    multi_results = [r for r in multi_results if len(r) < 120]
    if multi_results:
        all_results.append(("🔄 多步运算（深度恶臭）", multi_results[:6]))

    # ======== 方法四：67进制 ========
    base67_result = find_67base_expression(target)
    if base67_result:
        all_results.append(("🏛️ 67进制展开（学院派恶臭）", [base67_result]))

    # ======== 方法五：特殊梗检测 ========
    specials = []
    if target == 114514:
        specials.append("114514 = 67 × 67 × 67 - 67 × 67 - 67 × 6 + 7    🐶 恶臭之巅！野兽先辈！")
    elif target == 1919810:
        specials.append("1919810 = (((67+67)×(67×67-7)) + 6) × 6 + 67    😭 不要不要！")
    elif target == 67:
        specials.append("67 = 67    🦨 根本就是恶臭本体！")
    elif target == 6767:
        specials.append("6767 = 6767    🤯 双重恶臭，纯度极高！")
    if specials:
        all_results.append(("🎭 特殊梗检测", specials))

    # ======== 打印结果 ========
    if not all_results:
        print("  😢 没能找到合适的恶臭表达式...")
        print("  试试其他数字吧")
    else:
        count = 0
        for category, results in all_results:
            if count >= max_results:
                break
            print(f"  ┌─ {category}")
            for r in results[:min(len(results), max_results - count)]:
                print(f"  │  • {r}")
                count += 1
            print(f"  └─")
            print()

    print(f"  {'='*50}")
    print(f"  共找到 {sum(len(r) for _, r in all_results)} 种恶臭表达式")
    print(f"  {'='*50}\n")


# ============ 命令行入口 ============

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 stench67.py <目标数字>")
        print("示例: python3 stench67.py 114514")
        sys.exit(1)

    try:
        target = int(sys.argv[1])
        stench_number(target)
    except ValueError:
        print("❌ 请输入有效的整数")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 中断了恶臭化进程")
        sys.exit(0)
