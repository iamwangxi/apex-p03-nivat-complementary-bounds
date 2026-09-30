#!/usr/bin/env python3
"""Exact global anchor classification for the two strictness obstacles.

Independent of the producer and section checker. Also checks concrete dilations.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dot(n, z):
    return n[0]*z[0]+n[1]*z[1]


def solve(n, a, m, b):
    det = n[0]*m[1]-n[1]*m[0]
    x, y = Fraction(a*m[1]-n[1]*b, det), Fraction(n[0]*b-a*m[0], det)
    return (int(x), int(y)) if x.denominator == y.denominator == 1 else None


def bezout(a, b):
    if not b:
        return (1 if a > 0 else -1, 0)
    x, y = bezout(b, a % b)
    return y, x-a//b*y


def global_count(M, N, lines, L):
    S = list(product(range(M), range(N)))
    Q = [{dot(n, p) for p in S} for n, off, v, weight in lines]
    anchors = set()
    slope = 0
    while any(dot(n, (1, slope)) == 0 for n, off, v, weight in lines):
        slope += 1
    for rx, ry in product(range(L), repeat=2):
        q = 0
        while any(off-dot(n, (rx+L*q, ry+L*slope*q)) in Q[i]
                  for i, (n, off, v, weight) in enumerate(lines)):
            q += 1
        anchors.add((rx+L*q, ry+L*slope*q))
    for i, (n, off, v, weight) in enumerate(lines):
        bx, by = bezout(*n)
        assert dot(n, (bx, by)) == 1
        for t in Q[i]:
            for phase in range(L):
                origin = ((off-t)*bx+phase*v[0], (off-t)*by+phase*v[1]); q = 0
                while any(other_off-dot(other_n, (origin[0]+L*q*v[0], origin[1]+L*q*v[1])) in Q[j]
                          for j, (other_n, other_off, _, _) in enumerate(lines) if j != i):
                    q += 1
                z = (origin[0]+L*q*v[0], origin[1]+L*q*v[1])
                assert [j for j, (nn, oo, _, _) in enumerate(lines) if oo-dot(nn, z) in Q[j]] == [i]
                anchors.add(z)
    for i, j in combinations(range(len(lines)), 2):
        for ti, tj in product(Q[i], Q[j]):
            z = solve(lines[i][0], lines[i][1]-ti, lines[j][0], lines[j][1]-tj)
            if z is not None:
                anchors.add(z)
    patterns = set()
    for X, Y in anchors:
        pattern = []
        for x, y in S:
            z = X+x, Y+y
            value = sum((1 if weight == 'one' else int(z[0 if weight == 'even-x' else 1] % 2 == 0))
                        for n, off, v, weight in lines if dot(n, z) == off)
            assert value in (0, 1), 'supports must be disjoint'
            pattern.append(value)
        patterns.add(tuple(pattern))
    return len(patterns)


def main():
    rows = []
    for k, N in [(2, 7), (3, 6), (5, 12)]:
        lines = [((-1, 2*k), 0, (2*k, 1), 'one'), ((1, 2*k), k, (2*k, -1), 'one')]
        P = global_count(k, N, lines, 1)
        assert P == k*N+1
        rows.append({'kind': 'fixed-k narrow rectangles', 'k': k, 'N': N, 'patterns': P,
                     'formula': 'k*N+1', 'configuration_fixed_when_N_varies': True})
    lines = [((0, 1), 0, (1, 0), 'even-x'), ((1, 0), 1, (0, 1), 'even-y')]
    for M, N in [(5, 5), (6, 9), (30, 30)]:
        P = global_count(M, N, lines, 2)
        assert P == M*N+2*M+2*N+1
        rows.append({'kind': 'fixed sparse orthogonal lines', 'M': M, 'N': N, 'patterns': P,
                     'formula': 'M*N+2*M+2*N+1', 'configuration_fixed': True})
    dilations = []
    for n in range(20, 101, 5):
        S = {(x, y) for x in range(n+1) for y in range(n-x+1)}
        E = {z for z in S if all((z[0]+a, z[1]+b) in S for a, b in [(0, 0), (1, 0), (1, 2), (2, 2)])}
        K = len({y-4*x for x, y in E}); C = Counter(y-4*x for x, y in S)
        ell = max(min(C[t] for t in range(a, a+6)) for a in range(min(C)-6, max(C)+1))
        bound = (K+1)*(ell+1)
        assert K == 5*n-25 and ell == n//5 and bound == n*n+n//5-24
        quad = (n*n+17*n-52)//2; T = (n+1)*(n+2)//2+1
        assert bound > quad > T
        dilations.append({'n': n, 'K': K, 'ell': ell, 'SC': bound, 'quad': quad, 'T': T})
    (ROOT/'运行记录/障碍与无限族检查结果-v1.0.json').write_text(
        json.dumps({'passed': True, 'obstacles': rows, 'dilations': dilations,
                    'scope': 'finite exact global checks and integer geometry; infinite claims have manuscript proofs'},
                   ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    print('obstacles: '+str([r['patterns'] for r in rows])+'; 17 fixed triangle dilations: PASS')


if __name__ == '__main__':
    main()
