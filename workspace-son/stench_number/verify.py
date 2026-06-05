#!/usr/bin/env python3
"""Verify stench expressions and compute ratings."""
import math
import json
from datetime import datetime, timezone, timedelta

N = 20070521
tz = timezone(timedelta(hours=8))

def compute(expr_str):
    """Evaluate an expression string safely."""
    # Replace symbols
    s = expr_str.replace('×', '*').replace('−', '-').replace('÷', '/').replace('＋', '+').replace('－', '-').replace('＋', '+')
    return eval(s)

def count_occurrences(expr_str, target):
    """Count occurrences of target string in expression that are standalone numbers."""
    import re
    pattern = r'(?<!\d)' + str(target) + r'(?!\d)'
    matches = re.findall(pattern, expr_str)
    return len(matches)

def rate_expression(expr_str):
    """Rate a stench expression 1-10."""
    score = 0
    
    # 114 appearances (max +6 = 3×)
    c114 = count_occurrences(expr_str, 114)
    # Don't double-count 114 that's part of 114514
    c114514 = count_occurrences(expr_str, 114514)
    c114_standalone = c114  # since 114514 is already matched separately by regex
    
    score += min(c114_standalone * 2, 6)
    
    # 514 appearances (max +9 = 3×)
    c514 = count_occurrences(expr_str, 514)
    c514_standalone = c514  # 114514 doesn't match \b514\b
    score += min(c514_standalone * 3, 9)
    
    # 114514 complete (max +10 = 2×)
    score += min(c114514 * 5, 10)
    
    # Operation complexity
    has_pow = '²' in expr_str or '³' in expr_str or '^' in expr_str or '!' in expr_str or '阶乘' in expr_str
    if has_pow:
        score += 3
    else:
        score += 1  # +−×÷ only
    
    # Expression length (>5 operators → +1)
    ops = sum(1 for c in expr_str if c in '×÷＋−+×÷')
    if ops > 5:
        score += 1
    
    # Stench number ratio
    import re
    numbers = re.findall(r'\d+', expr_str)
    stench_set = {1, 4, 5, 11, 14, 15, 51, 54, 114, 514, 1145, 1451, 14514, 114514, 1145140, 1919810, 1145141919810}
    nums_int = [int(n) for n in numbers]
    if nums_int:
        ratio = sum(1 for n in nums_int if n in stench_set) / len(nums_int)
        if ratio > 0.7:
            score += 2
    
    # Convert to level
    if score <= 2:
        level = 1
        emoji = "🫵"
        label = "不够臭啊"
    elif score <= 5:
        level = max(3, score - 1)
        emoji = "💨"
        label = "微微发臭"
    elif score <= 8:
        level = score - 1
        emoji = "🤢"
        label = "有点味道了"
    elif score <= 12:
        level = score - 4
        emoji = "💩"
        label = "恶臭来袭"
    elif score <= 16:
        level = 9
        emoji = "🔥"
        label = "非常恶臭"
    else:
        level = 10
        emoji = "🏆"
        label = "究极恶臭！"
    
    return level, emoji, label, score

# Verified expressions:
expressions = [
    {
        "expr": "114514 × (114 + 54 + 5 + 1 + 1) + 514 × (54 + 5) + 5 × 54 − 5 × 5",
        "is_best": True
    },
    {
        "expr": "1145140 × 17 + 114514 × 5 + 514 × (54 + 5) + 5 × 54 − 5 × 5",
        "is_best": False
    },
    {
        "expr": "114514 × 100 + 114514 × 70 + 114514 × 5 + 514 × 54 + 514 × 5 + 5 × 54 − 5 × 5",
        "is_best": False
    },
    {
        "expr": "514 × (114 × 342 + 54 + 5) + 114 + 114 + 114 + 14 + 5 + 1 + 1",
        "is_best": False
    }
]

# Verify each
print(f"Target: {N}")
print("=" * 60)
for i, entry in enumerate(expressions):
    e = entry["expr"]
    # Normalize for eval
    eval_expr = e.replace('×', '*').replace('−', '-').replace('÷', '/')
    result = compute(eval_expr)
    ok = "✓" if result == N else "✗"
    level, emoji, label, score = rate_expression(e)
    tag = "📿 BEST" if entry["is_best"] else f"💩 #{i}"
    print(f"\n{tag}: {e}")
    print(f"   = {result} {ok}  (score={score}, level={level}/10 {emoji} {label})")

# Create the final result
print("\n\n=== FINAL OUTPUT ===")
best_expr = expressions[0]["expr"]
best_level, best_emoji, best_label, best_score = rate_expression(best_expr)

lines = []
lines.append(f"🤢 数字 {N} 的恶臭拆解：")
lines.append("")
lines.append(f"📿 最佳恶臭：")
lines.append(f"{N} = {best_expr}")
lines.append(f"恶臭等级：{best_level}/10 {best_emoji} {best_label}")
lines.append("")
lines.append(f"💩 其他恶臭组合：")
for i, entry in enumerate(expressions[1:], 1):
    e = entry["expr"]
    lev, em, lb, sc = rate_expression(e)
    lines.append(f"{N} = {e}")
lines.append("")
lines.append("--- ")
lines.append("🫵 你也是恶臭人了！")

for l in lines:
    print(l)

# Prepare for DB
expressions_json = json.dumps([e["expr"] for e in expressions])
timestamp = datetime.now(tz).isoformat()
print(f"\n\n=== DB INSERT ===")
print(f"input_number: {N}")
print(f"expressions: {expressions_json}")
print(f"requester_id: 6687D4D2D1F8EDA5231C6809B1A26204")
print(f"created_at: {timestamp}")
