#!/usr/bin/env python3
"""Evidence producer. Standard library only; never imports a checker."""
import json
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mul(p, q):
    r = defaultdict(int)
    for (x, y), a in p.items():
        for (u, v), b in q.items():
            r[x+u, y+v] += a*b
    return {k: v for k, v in r.items() if v}


def poly(v, coefficients):
    return {(j*v[0], j*v[1]): a for j, a in enumerate(coefficients) if a}


def records(p):
    return [[x, y, a] for (x, y), a in sorted(p.items())]


def bezout(a, b):
    if b == 0:
        return (1 if a > 0 else -1, 0)
    x, y = bezout(b, a % b)
    return y, x-(a//b)*y


def dot(n, z):
    return n[0]*z[0]+n[1]*z[1]


def fixture(name):
    if name in ('three-line', 'higher-order'):
        lines = [{'normal': [-2*i, 1], 'offset': i, 'v': [1, 2*i],
                  'weight': 'one'} for i in range(3)]
        coefficients = [[-1, 1]]*3
        if name == 'higher-order':
            lines[0]['weight'] = 'alternating-x'
            lines[1]['weight'] = 'even-x'
            coefficients = [[1, 1], [-1, 0, 1], [-1, 1]]
        background = 'zero'
        extra = {(0, 0): 1}
    elif name == 'background':
        lines = [{'normal': [0, 1], 'offset': 0, 'v': [1, 0], 'weight': 'one'},
                 {'normal': [1, 0], 'offset': 0, 'v': [0, 1], 'weight': 'one'}]
        coefficients = [[-1, 1]]*2
        background = 'checkerboard'
        extra = {(0, 0): 1, (1, 0): 1}
    else:
        raise ValueError(name)
    factors = [poly(l['v'], cs) for l, cs in zip(lines, coefficients)]
    phi = {(0, 0): 1}
    for p in factors:
        phi = mul(phi, p)
    return {'id': name, 'lines': lines, 'coefficients': coefficients,
            'background': background, 'phase_modulus': 1 if name == 'three-line' else 2,
            'phi': records(phi), 'f': records(mul(phi, extra)), 'extra': records(extra)}, factors, phi, extra


def points(spec):
    kind = spec['kind']
    if kind == 'rectangle':
        return sorted(product(range(spec['a']), range(spec['b'])))
    if kind == 'triangle':
        return sorted((x, y) for x in range(spec['n']+1) for y in range(spec['n']+1-x))
    if kind == 'point':
        return [(0, 0)]
    if kind == 'segment':
        return [(j, 2*j) for j in range(spec['n']+1)]
    raise ValueError(kind)


def weight(line, z):
    if line['weight'] == 'one':
        return 1
    if line['weight'] == 'alternating-x':
        return (-1)**(z[0] % 2)
    return int(z[0] % 2 == 0)


def solve(a, A, b, B):
    determinant = a[0]*b[1]-a[1]*b[0]
    x, y = Fraction(A*b[1]-a[1]*B, determinant), Fraction(a[0]*B-A*b[0], determinant)
    return (int(x), int(y)) if x.denominator == y.denominator == 1 else None


def global_events(S, config):
    """Enumerate hit strata, including all tangential/background residue phases."""
    lines, L = config['lines'], config['phase_modulus']
    Q = [sorted({dot(l['normal'], s) for s in S}) for l in lines]
    events = []
    k = 0
    while any(dot(l['normal'], (1, k)) == 0 for l in lines):
        k += 1
    direction = (L, L*k)
    for rx, ry in product(range(L), repeat=2):
        origin = (rx, ry)
        forbidden = set()
        for l, ts in zip(lines, Q):
            for t in ts:
                q = Fraction(l['offset']-t-dot(l['normal'], origin), dot(l['normal'], direction))
                if q.denominator == 1:
                    forbidden.add(int(q))
        step = 0
        while step in forbidden:
            step += 1
        events.append({'kind': 'zero', 'phase': [rx, ry], 'avoid_step': step,
                       'anchor': [rx+step*direction[0], ry+step*direction[1]]})
    for i, (l, ts) in enumerate(zip(lines, Q)):
        nx, ny = l['normal']; bx, by = bezout(nx, ny)
        assert nx*bx+ny*by == 1
        for t in ts:
            base = ((l['offset']-t)*bx, (l['offset']-t)*by)
            for phase in range(L):
                origin = (base[0]+phase*l['v'][0], base[1]+phase*l['v'][1])
                delta = (L*l['v'][0], L*l['v'][1]); forbidden = set()
                for j, (other, os) in enumerate(zip(lines, Q)):
                    if i != j:
                        for u in os:
                            q = Fraction(other['offset']-u-dot(other['normal'], origin), dot(other['normal'], delta))
                            if q.denominator == 1:
                                forbidden.add(int(q))
                step = 0
                while step in forbidden:
                    step += 1
                events.append({'kind': 'single', 'line': i, 'offset': t, 'phase': phase,
                               'avoid_step': step, 'anchor': [origin[0]+step*delta[0], origin[1]+step*delta[1]]})
    pairs = set()
    for i, j in combinations(range(len(lines)), 2):
        for a, b in product(Q[i], Q[j]):
            z = solve(lines[i]['normal'], lines[i]['offset']-a,
                      lines[j]['normal'], lines[j]['offset']-b)
            if z is not None:
                pairs.add(z)
    events += [{'kind': 'multiple', 'anchor': list(z)} for z in sorted(pairs)]
    return Q, events


def event_pattern(S, config, anchor, Q):
    """Producer reads the hit sections, adding weights and background by phase."""
    values = [(-1)**((anchor[0]+s[0]+anchor[1]+s[1]) % 2)
              if config['background'] == 'checkerboard' else 0 for s in S]
    for l, offsets in zip(config['lines'], Q):
        t = l['offset']-dot(l['normal'], anchor)
        if t in offsets:
            for j, s in enumerate(S):
                if dot(l['normal'], s) == t:
                    values[j] += weight(l, (anchor[0]+s[0], anchor[1]+s[1]))
    return tuple(values)


def sections(S, config, factors, phi, extra):
    SS = set(S); result = []
    for i, l in enumerate(config['lines']):
        g = extra.copy()
        for j, factor in enumerate(factors):
            if i != j:
                g = mul(g, factor)
        # A support reference is enough to bound the erosion candidates.
        ref = next(iter(g)); candidates = {(x-ref[0], y-ref[1]) for x, y in S}
        E = sorted(z for z in candidates if all((z[0]+q[0], z[1]+q[1]) in SS for q in g))
        vx, vy = l['v']; projection = lambda z: vx*z[1]-vy*z[0]
        cs = Counter(map(projection, S)); ce = Counter(map(projection, E))
        d = len(config['coefficients'][i])-1; epsilon = int(sum(config['coefficients'][i]) == 0)
        width = max(map(projection, phi))-min(map(projection, phi))
        K = sum(n >= d for n in ce.values())
        ell = max(min(cs[t] for t in range(a, a+width)) for a in range(min(cs)-width, max(cs)+1))
        result.append({'direction': l['v'], 'g': records(g), 'E': [list(z) for z in E],
                       'd': d, 'epsilon': epsilon, 'w': width, 'K': K, 'ell': ell,
                       'bound': (K+epsilon)*(ell+1)})
    return result


def dataset(name, spec, detailed):
    config, factors, phi, extra = fixture(name); S = points(spec)
    Q, events = global_events(S, config)
    representative = {}
    for event in events:
        p = event_pattern(S, config, event['anchor'], Q)
        representative.setdefault(p, event['anchor'])
    patterns = sorted(representative)
    result = {'configuration': config, 'window': spec, 'sections': sections(S, config, factors, phi, extra),
              'pattern_count': len(patterns), 'event_count': len(events),
              'projection_counts': list(map(len, Q))}
    if detailed:
        masks = sorted(sum(a << j for j, a in enumerate(p)) for p in patterns)
        size = (len(S)+7)//8
        by_mask = {sum(a << j for j, a in enumerate(p)): z for p, z in representative.items()}
        result.update({'points': [list(z) for z in S], 'events': events,
                       'patterns': [{'hex': hex(m), 'anchor': by_mask[m]} for m in masks],
                       'byte_width': size,
                       'pattern_sha256': sha256(b''.join(m.to_bytes(size, 'little') for m in masks)).hexdigest(),
                       'multiple_anchor_count': sum(e['kind'] == 'multiple' for e in events)})
        A = phi; RZ = sorted(z for z in S if all((z[0]+q[0], z[1]+q[1]) in set(S) for q in A))
        T = sorted(z for z in S if (z[0]+1, z[1]+1) in set(S))
        cross = defaultdict(int)
        for i, j in product(range(3), repeat=2):
            if i != j:
                a, b = config['lines'][i], config['lines'][j]
                z = solve(a['normal'], a['offset'], b['normal'], b['offset']-dot(b['normal'], (1, 1)))
                if z is not None:
                    cross[z] += 1
        J = defaultdict(int)
        for z, value in cross.items():
            for shift, coeff in A.items():
                J[z[0]-shift[0], z[1]-shift[1]] += value*coeff
        J = {z: v for z, v in J.items() if v}
        result.update({'RZ': [list(z) for z in RZ], 'Td': [list(z) for z in T],
                       'quad': len(S)+1-len(RZ)+len(T), 'cross': records(cross), 'J': records(J),
                       'analytic_rank': {'affine': len(S)+1-len(RZ), 'extended': len(S)+1-len(RZ)+len(T),
                                         'type': 'analytic proof plus exact geometry; no large numerical minor'}})
    return result


def main():
    triangle = dataset('three-line', {'kind': 'triangle', 'n': 30}, True)
    comparisons = [dataset('three-line', s, False) for s in
                   [{'kind': 'rectangle', 'a': 6, 'b': 9}, {'kind': 'rectangle', 'a': 30, 'b': 30},
                    {'kind': 'triangle', 'n': 1}, {'kind': 'triangle', 'n': 20}, {'kind': 'triangle', 'n': 50}]]
    stress = [dataset('higher-order', {'kind': 'rectangle', 'a': a, 'b': b}, False)
              for a in range(1, 9) for b in range(1, 9)]
    stress += [dataset('higher-order', {'kind': 'triangle', 'n': n}, False) for n in range(21)]
    stress += [dataset('background', {'kind': 'rectangle', 'a': 6, 'b': 9}, False)]
    stress += [dataset('higher-order', s, False) for s in
               [{'kind': 'point'}, {'kind': 'segment', 'n': 6}]]
    for filename, data in [('三角形全局证据-v1.0.json', triangle),
                           ('比较与压力测试-v1.0.json', {'comparisons': comparisons, 'stress': stress})]:
        (ROOT/'证据'/filename).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n')
    print(json.dumps({'triangle_patterns': triangle['pattern_count'], 'triangle_quad': triangle['quad'],
                      'triangle_SC': max(r['bound'] for r in triangle['sections']), 'stress_windows': len(stress)}))


if __name__ == '__main__':
    main()
