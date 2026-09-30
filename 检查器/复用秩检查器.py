#!/usr/bin/env python3
"""固定 Nivat 输入的独立证书验收；纯标准库，不读/导入任何生成器。"""
import copy
import hashlib
import itertools
import json
import math
import platform
import re
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent  # portable copy; historical paths are provenance only
CERT_NAMES = ["矩形6乘9-精确秩证书-v1.0.json", "删点2-4-精确秩证书-v1.0.json"]
EXPECTED_FILE_HASHES = [
    "258b88aea81a57f2587b2325534f8be9fe02c24e9a9b75de9ed857b9689cbd47",
    "2e158a8d04069badfed4f6e5b4941fd47540fd0c6e7630c91e9d6a317f64d942",
]
SOURCE_ALLOWLIST = {
    "drafts/Apex数学悬赏/03验证/旧基线/旧基线复现与全局覆盖证明-v1.0.md",
    "drafts/Apex数学悬赏/03验证/旧基线/全部模式与锚点.json",
    "drafts/Apex数学悬赏/03验证/旧基线/二次见证完整支撑.json",
    "drafts/Apex数学悬赏/03验证/深化三路任务书-v1.0.md",
    "collab/20260930-Apex数学悬赏后续方向.md",
}
UNREAD_GENERATOR = "drafts/Apex数学悬赏/03验证/二次位置加强/证书生成器.py"


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8"))


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def solve_two(n, a, m, b):
    """独立用 Cramer 公式解两个法向量方程，不沿用证书交点公式。"""
    det = n[0] * m[1] - n[1] * m[0]
    require(det != 0, "parallel lines in two-line solver")
    return (Fraction(a * m[1] - n[1] * b, det),
            Fraction(n[0] * b - a * m[0], det))


def integer_point(p):
    return tuple(int(t) for t in p) if all(t.denominator == 1 for t in p) else None


def hull(points):
    points = sorted(set(points))
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    halves = []
    for order in (points, list(reversed(points))):
        stack = []
        for p in order:
            while len(stack) >= 2 and cross(stack[-2], stack[-1], p) <= 0:
                stack.pop()
            stack.append(p)
        halves.append(stack[:-1])
    return halves[0] + halves[1]


def inside(p, polygon):
    return all((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]) >= 0
               for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def bounding_lattice(polygon):
    return itertools.product(range(min(p[0] for p in polygon), max(p[0] for p in polygon)+1),
                             range(min(p[1] for p in polygon), max(p[1] for p in polygon)+1))


def bareiss(matrix):
    """有主元交换的整数 Bareiss；每次除法检查余数为零。"""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "minor is not square")
    if not n:
        return 1
    a = [list(row) for row in matrix]
    require(all(type(t) is int for row in a for t in row), "minor entries not integers")
    previous, sign = 1, 1
    for k in range(n-1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[k], a[p] = a[p], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                value, rem = divmod(pivot*a[i][j]-a[i][k]*a[k][j], previous)
                require(rem == 0, "Bareiss non-exact division")
                a[i][j] = value
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]


def rational(text):
    require(isinstance(text, str) and re.fullmatch(r"-?\d+(?:/[1-9]\d*)?", text),
            "invalid exact rational encoding")
    return Fraction(text)


def components(config):
    require(config["base_field"] == "F_2" and config["coding"] == {"0": 0, "1": 1},
            "configuration field/coding mismatch")
    c = config["components"]
    require(len(c) == 3, "expected exactly three components")
    for i, item in enumerate(c):
        require(item["i"] == i and item["v"] == [1, 2*i] and
                item["normal"] == [-2*i, 1] and item["offset"] == i,
                "fixed line configuration mismatch")
        require(math.gcd(*item["v"]) == 1 and dot(item["normal"], item["v"]) == 0,
                "nonprimitive or invalid component period")
    require(config["case"] == "B" and config["tails"] == "all zero" and
            config["A_equals_D"] is True, "configuration semantics mismatch")
    return c


def eta(point, comps):
    return sum(dot(c["normal"], point) == c["offset"] for c in comps)


def bits(anchor, points, comps):
    result = tuple(eta(add(anchor, p), comps) for p in points)
    require(all(v in (0, 1) for v in result), "overlapping supports on integer lattice")
    return result


def operator(comps):
    polynomial = {(0, 0): 1}
    for c in comps:
        next_poly = defaultdict(int)
        for p, value in polynomial.items():
            next_poly[add(p, c["v"])] += value
            next_poly[p] -= value
        polynomial = {p: v for p, v in next_poly.items() if v}
    return polynomial


def check_configuration(cert):
    conf = cert["configuration"]
    require(canonical(conf) == cert["configuration_sha256"], "configuration digest mismatch")
    comps = components(conf)
    intersections = []
    for a, b in itertools.combinations(comps, 2):
        p = solve_two(a["normal"], a["offset"], b["normal"], b["offset"])
        require(p[0] == Fraction(-1, 2) and integer_point(p) is None,
                "supports not globally disjoint on Z^2")
        intersections.append([str(t) for t in p])
    require(Fraction(conf["pairwise_line_intersection_x"]) == Fraction(-1, 2),
            "intersection metadata mismatch")
    op = operator(comps)
    require(sum(op.values()) == 0, "D does not kill constants")
    # 对每个分量，按法向平移量聚合系数；恒等于零即在全平面消去该分量。
    for c in comps:
        grouped = defaultdict(int)
        for shift, coeff in op.items():
            grouped[dot(c["normal"], shift)] += coeff
        require(all(v == 0 for v in grouped.values()), "global Case B annihilation failed")
    return comps, op, {"pairwise_intersections": intersections,
                       "Case_B_global_operator_identity": True,
                       "component_period_groups": ["Z*(1,0)", "Z*(1,2)", "Z*(1,4)"],
                       "tails": "zero on both sides of each support line"}


def check_window(cert, comps):
    w = cert["window"]
    rectangle = [(x, y) for x in range(6) for y in range(9)]
    if cert["example_id"] == "rectangle_6x9":
        deleted = []
    elif cert["example_id"] == "rectangle_6x9_minus_2_4":
        deleted = [(2, 4)]
    else:
        raise Rejected("unknown fixed example")
    points = [p for p in rectangle if p not in deleted]
    require(w["points"] == [list(p) for p in points] and
            w["deleted_points"] == [list(p) for p in deleted], "window point list mismatch")
    require(cert["source_rectangle_points"] == [list(p) for p in rectangle],
            "source rectangle point list mismatch")
    shape = hull(points)
    vertices = {(0, 0)}
    for c in comps:
        vertices |= {add(p, c["v"]) for p in vertices}
    z = hull(vertices)
    require(w["convex_hull_vertices_ccw"] == [list(p) for p in shape], "window hull mismatch")
    require(w["Z_vertices_ccw"] == [list(p) for p in z], "Z hull mismatch")
    lattice = {p for p in bounding_lattice(shape) if inside(p, shape)}
    require(w["is_lattice_convex"] is (lattice == set(points)), "lattice convexity mismatch")
    require(w["displacement"] == [1, 1], "displacement mismatch")
    d = tuple(w["displacement"])
    legal = [p for p in points if add(p, d) in set(points)]
    require(w["legal_quadratic_starts"] == [list(p) for p in legal],
            "legal quadratic position list mismatch")
    # 0 in Z: every feasible r belongs to Conv(S); exact hull inclusion completes R.
    require(inside((0, 0), z), "zero missing from Z")
    rset = sorted(p for p in lattice if all(inside(add(p, v), shape) for v in z))
    require(w["R_Z_S"] == [list(p) for p in rset], "R_Z_S enumeration mismatch")
    return rectangle, points, legal, rset, z


def reconstruct_global(points, comps):
    """全局分类：零线、单线、任意一对命中线的唯一交点；无有限框采样。"""
    offsets = [sorted({dot(c["normal"], p) for p in points}) for c in comps]
    patterns, keys, event_anchors, pair_anchors = set(), set(), {}, set()
    def register(key, anchor):
        require(key not in keys, "duplicate independently generated event")
        keys.add(key)
        event_anchors[key] = anchor
        patterns.add(bits(anchor, points, comps))
    forbidden = {c["offset"]-b for c, os in zip(comps, offsets) for b in os}
    t = 0
    while t in forbidden:
        t += 1
    register(("zero_lines",), (0, t))
    for i, c in enumerate(comps):
        for b in offsets[i]:
            origin = (0, c["offset"]-b)
            forbidden = set()
            for j, other in enumerate(comps):
                if i != j:
                    slope = dot(other["normal"], c["v"])
                    require(slope != 0, "parallel support directions")
                    for other_b in offsets[j]:
                        t = Fraction(other["offset"]-other_b-dot(other["normal"], origin), slope)
                        if t.denominator == 1:
                            forbidden.add(int(t))
            t = 0
            while t in forbidden:
                t += 1
            anchor = add(origin, (t*c["v"][0], t*c["v"][1]))
            register(("one_line", i, b), anchor)
    for i, j in itertools.combinations(range(len(comps)), 2):
        for b, e in itertools.product(offsets[i], offsets[j]):
            anchor = integer_point(solve_two(comps[i]["normal"], comps[i]["offset"]-b,
                                            comps[j]["normal"], comps[j]["offset"]-e))
            if anchor is not None:
                register(("two_lines", i, j, b, e), anchor)
                pair_anchors.add(anchor)
    return sorted(patterns), offsets, keys, event_anchors, len(pair_anchors)


def check_patterns(cert, rectangle, points, comps):
    expected, offsets, keys, anchors, pair_count = reconstruct_global(points, comps)
    source_expected, _, _, _, _ = reconstruct_global(rectangle, comps)
    recorded = cert["patterns"]
    require([tuple(p["bits"]) for p in recorded] == expected,
            "global pattern set mismatch (omission, spurious pattern, duplicate or order)")
    require(canonical(recorded) == cert["patterns_sha256"], "pattern digest mismatch")
    require([tuple(p["bits"]) for p in cert["source_rectangle_patterns"]] == source_expected,
            "source rectangle global patterns mismatch")
    for rows, coordinates in [(recorded, points), (cert["source_rectangle_patterns"], rectangle)]:
        for row in rows:
            require(all(type(t) is int and t in (0, 1) for t in row["bits"]), "invalid bit value")
            require(bits(row["anchor"], coordinates, comps) == tuple(row["bits"]),
                    "stored anchor does not realize its pattern")
    coverage = cert["coverage"]
    require(coverage["offsets"] == offsets, "line offsets mismatch")
    seen = set()
    for ev in coverage["events"]:
        kind = ev["type"]
        if kind == "zero_lines":
            key = (kind,)
        elif kind == "one_line":
            require(len(ev["lines"]) == len(ev["offsets"]) == 1, "malformed one-line event")
            key = (kind, ev["lines"][0], ev["offsets"][0])
        elif kind == "two_lines":
            require(len(ev["lines"]) == len(ev["offsets"]) == 2, "malformed two-line event")
            key = (kind, *ev["lines"], *ev["offsets"])
        else:
            raise Rejected("unrecognized coverage event")
        require(key in keys and key not in seen, "invalid or duplicate coverage event")
        seen.add(key)
        anchor = tuple(ev["anchor"])
        hits = [i for i, c in enumerate(comps) if c["offset"]-dot(c["normal"], anchor) in offsets[i]]
        if kind == "zero_lines":
            require(hits == [], "zero-line event hits a support line")
        else:
            require((hits == ev["lines"] if kind == "one_line" else all(i in hits for i in ev["lines"])),
                    "coverage event line classification mismatch")
            for i, b in zip(ev["lines"], ev["offsets"]):
                require(comps[i]["offset"]-dot(comps[i]["normal"], anchor) == b,
                        "coverage event offset mismatch")
        if kind == "two_lines":
            require(anchor == anchors[key], "two-line event is not its unique integer intersection")
        index = ev["pattern_index"]
        require(type(index) is int and 0 <= index < len(recorded), "coverage pattern index out of range")
        require(tuple(recorded[index]["bits"]) == bits(anchor, points, comps), "coverage pattern row mismatch")
    require(seen == keys, "coverage event omission")
    counts = dict(Counter(k[0] for k in keys))
    require(coverage["event_counts"] == counts, "coverage event counts mismatch")
    indices = [rectangle.index(p) for p in points]
    require(cert["restriction_coordinate_indices"] == indices, "restriction coordinates mismatch")
    restricted = [tuple(row[i] for i in indices) for row in source_expected]
    require(sorted(set(restricted)) == expected, "rectangle restriction does not cover target patterns")
    lookup = {p: i for i, p in enumerate(expected)}
    mapping = [lookup[p] for p in restricted]
    require(cert["source_rectangle_to_target_pattern_index"] == mapping, "restriction mapping mismatch")
    inverse = defaultdict(list)
    for i, target in enumerate(mapping):
        inverse[target].append(i)
    require(all(row["source_rectangle_pattern_indices"] == inverse[i] for i, row in enumerate(recorded)),
            "inverse restriction groups mismatch")
    return {"pattern_count": len(expected), "coverage_event_counts": counts,
            "coverage_event_total": len(keys), "distinct_two_line_anchors": pair_count,
            "source_pattern_count": len(source_expected),
            "restriction_group_sizes": dict(Counter(len(v) for v in inverse.values()))}


def sparse_records(values, field="point", coeff="value"):
    return [{field: list(p), coeff: values[p]} for p in sorted(values)]


def check_witness(cert, comps, op, z):
    w = cert["witness"]
    d = tuple(cert["window"]["displacement"])
    require(w["translation_convention"] == "T^h f(z)=f(z+h)" and w["d"] == list(d),
            "witness translation/displacement mismatch")
    require(w["V"] == [c["v"] for c in comps], "witness directions mismatch")
    require(sub(w["q1"], w["q0"]) == d and inside(w["q0"], z) and inside(w["q1"], z),
            "witness endpoints not in Z or displacement mismatch")
    require(w["difference_operator"] == sparse_records(op, "shift", "coefficient"),
            "difference operator coefficients mismatch")
    cross = defaultdict(int)
    expected_solutions = []
    for i, a in enumerate(comps):
        for j, b in enumerate(comps):
            if i == j:
                # 本固定例的三项甚至恒为零；一般原理只要求沿 vi 周期而被 D 消去。
                require(dot(a["normal"], d) != 0, "unexpected nonzero diagonal term")
                continue
            p = integer_point(solve_two(a["normal"], a["offset"],
                                        b["normal"], b["offset"]-dot(b["normal"], d)))
            numerator = i-j+d[1]-2*j*d[0]
            denominator = 2*(j-i)
            expected_solutions.append({"i": i, "j": j,
                                       "integer_solution": list(p) if p is not None else None,
                                       "numerator": numerator, "denominator": denominator})
            if p is not None:
                cross[p] += 1
    require(w["ordered_cross_pair_solutions"] == expected_solutions, "cross-pair equations mismatch")
    require(w["cross_term_support"] == sparse_records(cross), "cross-term support mismatch")
    # 独立采用逐因子稀疏差分；不是按证书给定的展开系数卷积。
    current = dict(cross)
    for c in comps:
        nxt = defaultdict(int)
        for p, value in current.items():
            nxt[sub(p, c["v"])] += value
            nxt[p] -= value
        current = {p: value for p, value in nxt.items() if value}
    require(current and w["entire_J_support"] == sparse_records(current), "entire J support mismatch")
    possible = {sub(p, shift) for p in cross for shift in op}
    for p in possible:
        direct = sum(coef*eta(add(p, shift), comps)*eta(add(add(p, shift), d), comps)
                     for shift, coef in op.items())
        require(direct == current.get(p, 0), "J direct-pixel evaluation mismatch")
    nz = w["nonzero_witness"]
    require(current.get(tuple(nz["point"]), 0) == nz["value"] != 0, "nonzero J witness failed")
    return {"ordered_cross_pairs": len(expected_solutions), "cross_support_size": len(cross),
            "entire_J_support_size": len(current), "candidate_support_points": len(possible),
            "nonzero_witness": nz, "global_support_completeness": True}


def check_matrix(block, pattern_rows, points, legal, extended):
    index = {p: i for i, p in enumerate(points)}
    cols = [{"kind": "constant", "value": 1}]
    cols += [{"kind": "linear", "point": list(p), "pattern_coordinate_index": i}
             for i, p in enumerate(points)]
    if extended:
        cols += [{"kind": "quadratic", "start": list(p), "end": list(add(p, (1, 1))),
                  "pattern_coordinate_indices": [index[p], index[add(p, (1, 1))]]} for p in legal]
    require(block["column_definitions"] == cols, "matrix column definitions mismatch")
    recomputed = []
    for pattern in pattern_rows:
        row = [1] + pattern["bits"][:]
        if extended:
            row += [pattern["bits"][index[p]] * pattern["bits"][index[add(p, (1, 1))]] for p in legal]
        recomputed.append(row)
    matrix = block["entries"]
    require(matrix == recomputed and all(type(v) is int for row in matrix for v in row),
            "full reconstructed matrix mismatch")
    require(block["canonical_entries_sha256"] == canonical(matrix), "matrix digest mismatch")
    m, n = len(matrix), len(cols)
    require(block["dimensions"] == [m, n], "matrix dimensions mismatch")
    rc = block["rank_certificate"]
    r = rc["rank"]
    require(rc["field"] == "Q" and type(r) is int and 0 <= r <= min(m, n), "invalid rational rank")
    minor = rc["minor"]
    rows, columns = minor["row_indices"], minor["column_indices"]
    for indices, bound in [(rows, m), (columns, n)]:
        require(len(indices) == len(set(indices)) == r and
                all(type(i) is int and 0 <= i < bound for i in indices), "invalid minor indices")
    determinant = bareiss([[matrix[i][j] for j in columns] for i in rows])
    require(re.fullmatch(r"-?\d+", minor["determinant"]) is not None and
            determinant == int(minor["determinant"]) != 0, "exact minor determinant mismatch")
    kernel = rc["right_kernel"]
    free = kernel["free_columns"]
    require(len(free) == len(set(free)) == n-r and all(type(i) is int and 0 <= i < n for i in free),
            "invalid free coordinates")
    vectors = kernel["vectors"]
    require(len(vectors) == n-r and all(len(v) == n for v in vectors), "kernel dimensions mismatch")
    products = 0
    for j, encoded in enumerate(vectors):
        vector = [rational(t) for t in encoded]
        require(all(vector[c] == int(j == k) for k, c in enumerate(free)), "kernel free coordinates not identity")
        # 清分母后执行整数乘法，绝不以浮点容差近似 0。
        denominator = 1
        for t in vector:
            denominator = math.lcm(denominator, t.denominator)
        integers = [int(t*denominator) for t in vector]
        require(all(sum(a*b for a, b in zip(row, integers)) == 0 for row in matrix),
                "right kernel multiplication nonzero")
        products += m
    require(kernel["free_coordinate_matrix"] == "identity", "kernel identity metadata mismatch")
    return {"dimensions": [m, n], "exact_Q_rank": r, "minor_order": r,
            "integer_determinant": determinant, "kernel_vectors": len(vectors),
            "kernel_row_dot_products": products, "rank_lower_bound": r,
            "rank_upper_bound": n-len(vectors), "free_coordinate_matrix_verified": "identity"}


def check_certificate(cert):
    require(cert["schema"] == "nivat-all-legal-quadratic-rank-certificate" and
            cert["schema_version"] == "1.0", "schema mismatch")
    comps, op, config_result = check_configuration(cert)
    rectangle, points, legal, rset, z = check_window(cert, comps)
    pattern_result = check_patterns(cert, rectangle, points, comps)
    witness_result = check_witness(cert, comps, op, z)
    matrices = {name: check_matrix(cert["matrices"][name], cert["patterns"], points, legal, extended)
                for name, extended in [("linear", False), ("extended", True)]}
    linear_rank, extended_rank = [matrices[name]["exact_Q_rank"] for name in ("linear", "extended")]
    require(extended_rank-linear_rank == len(legal), "quadratic dimension increment mismatch")
    counts = {"window_size": len(points), "R_Z_S_count": len(rset), "T_d_S_count": len(legal),
              "global_pattern_count": len(cert["patterns"]),
              "lemma_2_5_lower_bound": len(points)+1-len(rset),
              "all_legal_positions_lower_bound": len(points)+1-len(rset)+len(legal),
              "actual_linear_rank": linear_rank, "actual_extended_rank": extended_rank,
              "original_theorem_A_bound_if_applicable": len(points)+1 if not cert["window"]["deleted_points"] else None}
    require(cert["counts_and_bounds"] == counts, "counts or bounds mismatch")
    return {"example_id": cert["example_id"], "configuration": config_result,
            "global_coverage": pattern_result, "witness": witness_result,
            "matrices": matrices, "counts_and_bounds": counts}


# Copied mathematical checker; the workspace-dependent main was omitted.

def negative_controls(original):
    def matrix(c):
        m = c["matrices"]["extended"]
        m["entries"][0][0] += 1
        m["canonical_entries_sha256"] = canonical(m["entries"])
    def kernel(c):
        k = c["matrices"]["linear"]["rank_certificate"]["right_kernel"]
        k["vectors"][0][0] = str(rational(k["vectors"][0][0])+1)
    def minor(c):
        m = c["matrices"]["linear"]["rank_certificate"]["minor"]
        m["determinant"] = str(int(m["determinant"])+1)
    def omission(c):
        c["patterns"].pop()
        c["patterns_sha256"] = canonical(c["patterns"])
    def witness(c):
        c["witness"]["entire_J_support"][0]["value"] += 1
    def legal(c):
        c["window"]["legal_quadratic_starts"].pop()
    def event(c):
        c["coverage"]["events"].pop()
    def mapping(c):
        c["source_rectangle_to_target_pattern_index"][0] = 1
    tests = [("矩阵条目且同步摘要", matrix, "full reconstructed matrix mismatch"),
             ("右核非自由坐标", kernel, "right kernel multiplication nonzero"),
             ("下界子式行列式", minor, "exact minor determinant mismatch"),
             ("模式漏项且同步摘要", omission, "global pattern set mismatch"),
             ("J 支撑系数", witness, "entire J support mismatch"),
             ("合法二次起点漏项", legal, "legal quadratic position list mismatch"),
             ("全局覆盖事件漏项", event, "coverage event omission"),
             ("删点来源映射", mapping, "restriction mapping mismatch")]
    results = []
    for name, mutate, expected_message in tests:
        damaged = copy.deepcopy(original)
        mutate(damaged)
        try:
            check_certificate(damaged)
        except Rejected as error:
            require(expected_message in str(error), "negative control failed for unexpected reason: " + str(error))
            results.append({"name": name, "rejected": True, "reason": str(error), "memory_only": True})
        else:
            raise Rejected("negative control escaped detection: " + name)
    return results

