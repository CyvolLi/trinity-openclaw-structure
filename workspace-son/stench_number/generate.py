#!/usr/bin/env python3
"""Generate stench number expressions for a given target number."""

import math
import random

TARGET = 1998914

BASE_NUMS = [1, 5, 4, 11, 14, 15, 51, 54]
EXT_NUMS = [114, 514, 1145, 1451, 14514, 114514, 1145140]
SPECIAL = [1919810, 1145141919810]
ALL_NUMS = sorted(set(BASE_NUMS + EXT_NUMS), reverse=True)

def try_multiply_divide(target, depth=0, max_depth=3):
    """Try using multiplication/division with big numbers."""
    if depth > max_depth:
        return None
    
    results = []
    
    # Try 114514 × k approach
    for k in range(1, 200):
        base = 114514 * k
        if base > target * 2:
            break
        diff = target - base
        if diff == 0:
            results.append((f"114514 × {k}", k, 0, "big"))
        elif abs(diff) < 100000:
            results.append((f"114514 × {k}", k, diff, "big"))
    
    # Try 514 × k approach
    for k in range(1, 5000):
        base = 514 * k
        if base > target * 2:
            break
        diff = target - base
        if diff == 0:
            results.append((f"514 × {k}", k, 0, "five"))
        elif abs(diff) < 5000:
            results.append((f"514 × {k}", k, diff, "five"))
    
    # Try 114 × k approach
    for k in range(1, 20000):
        base = 114 * k
        if base > target * 2:
            break
        diff = target - base
        if diff == 0:
            results.append((f"114 × {k}", k, 0, "hun"))
        elif abs(diff) < 2000:
            results.append((f"114 × {k}", k, diff, "hun"))
    
    # Try 1145 × k approach
    for k in range(1, 2000):
        base = 1145 * k
        if base > target * 2:
            break
        diff = target - base
        if diff == 0:
            results.append((f"1145 × {k}", k, 0, "thou"))
        elif abs(diff) < 5000:
            results.append((f"1145 × {k}", k, diff, "thou"))
    
    return results

def decompose_small(n, used_114_count=0, used_514_count=0):
    """Decompose a small number into base stench numbers."""
    if n == 0:
        return [], used_114_count, used_514_count
    if n in ALL_NUMS:
        terms = [str(n)]
        c114 = used_114_count + (1 if n == 114 else 0)
        c514 = used_514_count + (1 if n == 514 else 0)
        return terms, c114, c514
    
    # Greedy approach with larger numbers first
    terms = []
    remaining = abs(n)
    sign = 1 if n >= 0 else -1
    c114 = used_114_count
    c514 = used_514_count
    
    for num in ALL_NUMS:
        while remaining >= num:
            terms.append(str(num))
            remaining -= num
            if num == 114: c114 += 1
            if num == 514: c514 += 1
    
    if remaining > 0:
        # Try to adjust with smaller numbers
        for num in [54, 51, 15, 14, 11, 5, 4, 1]:
            while remaining >= num:
                terms.append(str(num))
                remaining -= num
    
    if sign == -1:
        return [f"-{t}" for t in terms], c114, c514
    return terms, c114, c514

def build_expression(target):
    """Build multiple stench expressions for target."""
    expressions = []
    
    # ---- Expression 1: 114514 × 17 + correction ----
    k = target // 114514  # 17
    remainder = target - 114514 * k  # 52176
    # Decompose remainder
    terms_r, c114_1, c514_1 = decompose_small(remainder)
    if remainder > 0 and terms_r:
        expr = f"114514 × {k} + {' + '.join(terms_r)}"
        score = c114_1 * 2 + c514_1 * 3 + (2 if '114514' in expr else 0)
        ops_count = 1 + len(terms_r)  # × and + operations
        complexity = 1  # basic ops
        total_score = score + complexity + (1 if ops_count > 5 else 0)
        expressions.append((expr, total_score, c114_1, c514_1))
    
    # ---- Expression 2: 1145140 + 858574 + correction ----
    # 1998914 = 1145140 + 853774... let me calculate
    # 1145140 + 853774 = 1998914
    # 853774 = ?
    # 514 × 1661 = 853, 754... let me compute
    # Actually let me try a different approach: factor the number
    
    # 1998914 = 2 × 7 × 19 × 103 ×... let me check
    # 1998914 / 2 = 999457
    # 999457 = ?
    
    # ---- Expression 2: Try 114514 × 17 + 514 × 101 + correction ----
    k1 = 17
    k2 = (target - 114514 * k1) // 514  # 52176 // 514 = 101
    r2 = target - 114514 * k1 - 514 * k2  # 52176 - 514 * 101 = 52176 - 51914 = 262
    terms_r2, c114_2, c514_2 = decompose_small(r2)
    if terms_r2:
        expr = f"114514 × {k1} + 514 × {k2} + {' + '.join(terms_r2)}"
        score = (c114_2 + 1) * 2 + (c514_2 + 1) * 3
        score += 5  # contains 114514
        expressions.append((expr, score, c114_2 + 1, c514_2 + 1))
    
    # ---- Expression 3: Using 114 × something ----
    # 1998914 / 114 = 17534.33...
    # 114 × 17534 = 114 × 17000 + 114 × 534 = 1938000 + 60876 = 1998876
    # remainder = 1998914 - 1998876 = 38
    # 38 = 15 + 14 + 5 + 4
    thirds_k = target // 114
    thirds_r = target - 114 * thirds_k
    terms_r3, c114_3, c514_3 = decompose_small(thirds_r)
    if terms_r3:
        expr = f"114 × {thirds_k} + {' + '.join(terms_r3)}"
        c114_3 += 1  # the 114 in the expression
        score = c114_3 * 2
        expressions.append((expr, score, c114_3, 0))
    
    # ---- Expression 4: Using 514 approach ----
    k4 = target // 514  # 3888
    r4 = target - 514 * k4
    terms_r4, c114_4, c514_4 = decompose_small(r4)
    if terms_r4:
        expr = f"514 × {k4} + {' + '.join(terms_r4)}"
        c514_4 += 1
        score = c514_4 * 3
        expressions.append((expr, score, 0, c514_4))
    
    # ---- Expression 5: Mixed approach with several 114s and 514s ----
    # 1998914 = 514 × 3888 + 114 + 114 + 114 + 114 + 114 + ...
    # Let me try: 1998914 = 114514 × 17 + 514 + 514 + ... + correction
    k5a = 17  # 114514 × 17
    remaining = target - 114514 * k5a  # 52176
    k5b = remaining // 514  # 101
    remaining2 = remaining - 514 * k5b  # 262
    # 262 = 114 + 114 + 34, but 34 not in set
    # 262 = 114 + 54 + 51 + 15 + 14 + 11 + 1 + 1 + 1
    terms_r5 = ["114", "54", "51", "15", "14", "11", "1", "1", "1"]
    expr5 = f"114514 × {k5a} + 514 × {k5b} + 114 + 54 + 51 + 15 + 14 + 11 + 1 + 1 + 1"
    c114_5 = 2  # the 114 and one from 114514
    c514_5 = 1 + 1  # the 514 from 114514 and one 514 term
    # Actually let me just count 114514 as one term
    
    # Let me think about this differently for counting purposes
    # 114514 × 17 → counts as 114514 appearing once
    # 514 × 101 → counts as 514 appearing (the factor 514)
    # Then remaining terms
    
    score5 = 5  # 114514 base
    c114_5_count = 1  # the 114 in the remaining sum
    c514_5_count = 2  # the 514 from 114514 and the standalone 514
    score5 += c114_5_count * 2 + c514_5_count * 3
    score5 += 1  # basic ops (>5 operators)
    expressions.append((expr5, score5, c114_5_count, c514_5_count))
    
    return expressions[:5]

def format_with_operators(expr_str):
    """Replace * and / with × and ÷ for display."""
    return expr_str.replace('*', '×').replace('/', '÷')

def calculate_grade(total_score):
    """Calculate stench grade 1-10."""
    if total_score >= 17:
        return (10, "🏆 究极恶臭！")
    elif total_score >= 13:
        return (9, "🔥 非常恶臭")
    elif total_score >= 9:
        return (7, "💩 恶臭来袭")
    elif total_score >= 6:
        return (5, "🤢 有点味道了")
    elif total_score >= 3:
        return (3, "💨 微微发臭")
    else:
        return (1, "🫵 不够臭啊")

def main():
    target = TARGET
    
    if target == 114514:
        print("PERFECT_HIT")
        return
    
    expressions = build_expression(target)
    
    # Deduplicate and sort by score
    seen = set()
    unique_exprs = []
    for expr, score, c114, c514 in expressions:
        if expr not in seen:
            seen.add(expr)
            unique_exprs.append((expr, score, c114, c514))
    
    unique_exprs.sort(key=lambda x: -x[1])
    
    # Take top 4
    top_exprs = unique_exprs[:4]
    
    for i, (expr, score, c114, c514) in enumerate(top_exprs):
        grade_num, grade_emoji = calculate_grade(score)
        print(f"EXPR:{i}:{expr}")
        print(f"SCORE:{i}:{score}")
        print(f"GRADE:{i}:{grade_num}/10 {grade_emoji}")
        print(f"C114:{i}:{c114}")
        print(f"C514:{i}:{c514}")

if __name__ == "__main__":
    main()
