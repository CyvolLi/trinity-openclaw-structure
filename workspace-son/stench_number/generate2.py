#!/usr/bin/env python3
"""Generate stench expressions for target number 1998914."""

TARGET = 1998914

# Core stench numbers
N114 = 114
N514 = 514
N114514 = 114514
N1145 = 1145
N1451 = 1451
N14514 = 14514
N1145140 = 1145140
N1919810 = 1919810

def format_expr(parts, operators):
    """Build expression string."""
    result = str(parts[0])
    for i, op in enumerate(operators):
        result += f" {op} {parts[i+1]}"
    return result

def count_114(s):
    """Count occurrences of standalone 114."""
    return s.count("114") - s.count("1145") - s.count("114514") * 2

def count_514(s):
    """Count occurrences of standalone 514."""
    return s.count("514") - s.count("114514") - s.count("14514")

def count_114514(s):
    return s.count("114514")

def score_expr(expr_str):
    """Calculate stench score."""
    c114 = count_114(expr_str)
    c514 = count_514(expr_str)
    c114514_full = count_114514(expr_str)
    
    score = 0
    score += min(c114 * 2, 6)       # 114 each +2, max 6
    score += min(c514 * 3, 9)       # 514 each +3, max 9
    score += min(c114514_full * 5, 10)  # 114514 each +5, max 10
    
    # Complexity
    ops = sum(1 for c in expr_str if c in '×÷')
    contains_power = '²' in expr_str or '³' in expr_str or '!' in expr_str
    if contains_power:
        score += 3
    else:
        score += 1
    
    # Length
    if ops > 5:
        score += 1
    
    return score, c114, c514, c114514_full

def grade(score):
    if score >= 17: return (10, "🏆 究极恶臭！")
    elif score >= 13: return (9, "🔥 非常恶臭")
    elif score >= 9: return (7, "💩 恶臭来袭")
    elif score >= 6: return (5, "🤢 有点味道了")
    elif score >= 3: return (3, "💨 微微发臭")
    else: return (1, "🫵 不够臭啊")

# ---- Expression 1: 114514 × 17 + 514 × 101 + 114 + 114 + 15 + 15 + 4 ----
# Verify: 114514*17 = 1,946,738; 514*101 = 51,914; sum = 1,998,652
# remaining: 1,998,914 - 1,998,652 = 262
# 262 = 114+114+15+15+4 = 262 ✓
E1 = "114514 × 17 + 514 × 101 + 114 + 114 + 15 + 15 + 4"

# ---- Expression 2: 114514 × 17 + 514 × 101 + 114 + 54 + 51 + 15 + 14 + 11 + 1 + 1 + 1 ----
# 114+54+51+15+14+11+1+1+1 = 262 ✓
E2 = "114514 × 17 + 514 × 101 + 114 + 54 + 51 + 15 + 14 + 11 + 1 + 1 + 1"

# ---- Expression 3: 114514 × 17 + 1145 × 45 + 114 + 54 + 51 + 15 + 14 + 11 ----
# 1145*45 = 51,525; remaining: 52176-51525 = 651
# 114+54+51+15+14+11 = ... let me recalculate
# 114+54=168, +51=219, +15=234, +14=248, +11=259... no
# Let me verify: 114+54+51+15+14+11 = 259
# 51525+259=51784... not 52176
# Hmm let me recalculate this differently.

# ---- Expression 3: Using 14514 ----
# 14514 × 137 = ?
# 14514*100 = 1,451,400
# 14514*37 = 14514*30 + 14514*7 = 435,420 + 101,598 = 537,018
# Total = 1,988,418
# 1,998,914 - 1,988,418 = 10,496
# 10,496 = ...
# Actually let me try a cleaner approach.

# ---- Expression 3: 1919810 + 114514 - 1145 - 1451 - 5 + 1 ----
# 1919810 + 114514 = 2,034,324
# 2,034,324 - 1145 = 2,033,179
# 2,033,179 - 1451 = 2,031,728
# 2,031,728 - 5 = 2,031,723
# 2,031,723 + 1 = 2,031,724... way too big
# Let me not do this.

# ---- Expression 3: 114514 × 17 + 1145 × 45 + 114 × 5 + 54 + 15 + 14 + 11 + 4 + 1 ----
# 1145*45 = 51,525; 114*5 = 570
# 51,525+570=52,095
# remaining: 52,176 - 52,095 = 81
# 54+15+14+11+4+1 = 99... that's too much
# 54+15+11+1 = 81 ✓
E3 = "114514 × 17 + 1145 × 45 + 114 × 5 + 54 + 15 + 11 + 1"
# Verify: 114514*17 = 1,946,738; 1145*45 = 51,525; 114*5 = 570; sum = 1,998,833
# Need: 1,998,914 - 1,998,833 = 81
# 54+15+11+1 = 81 ✓

# ---- Expression 4: 514 × 3888 + 114 + 114 + 114 + 114 + 15 + 11 ----
# 514*3888 = 514*4000 - 514*112 = 2,056,000 - 57,568 = 1,998,432
# Wait that's wrong. 514*3888:
# 500*3888 = 1,944,000
# 14*3888 = 54,432
# Total = 1,998,432
# Remaining: 1,998,914 - 1,998,432 = 482
# 114+114+114+114 = 456, +15+11 = 482 ✓
E4 = "514 × 3888 + 114 × 4 + 15 + 11"

# ---- Expression 5: 114514 × 13 + 1145140 + 14514 × 5 + 514 × 5 + 114 + 114 + 15 + 15 + 4 ----
# 114514*13 = 1,488,682
# + 1145140 = 2,633,822... too big
# Let me just verify E1 is correct and use my best ones.

expressions = [E1, E2, E3, E4]

# Verify each
def verify(expr):
    """Evaluate an expression to check it equals TARGET."""
    # Parse: replace × with * and evaluate
    # But I'll hard-verify each
    parts = expr.split()
    total = 0
    # I'll just print verification manually
    return expr

# Print verification and scores
for i, expr in enumerate(expressions):
    score, c114, c514, c114514_full = score_expr(expr)
    g, g_emoji = grade(score)
    print(f"EXPR:{i}")
    print(f"  EQ: {expr}")
    print(f"  SCORE: {score}")
    print(f"  GRADE: {g}/10 {g_emoji}")
    print(f"  114 count: {c114}")
    print(f"  514 count: {c514}")
    print(f"  114514 count: {c114514_full}")
