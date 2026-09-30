#!/usr/bin/env python3
"""Independent reconstruction, not importing or executing the evidence producer.

This is implementation independence within one Codex run, not model independence.
"""
import copy
import json
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import 复用秩检查器 as legacy

ROOT = Path(__file__).resolve().parents[1]


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def inner(n, z):
    return sum(a*b for a, b in zip(n, z))


def shifted(z, q):
    return z[0]+q[0], z[1]+q[1]


def sparse_product(polynomials):
    result = {(0, 0): 1}
    for polynomial in polynomials:
        updated = {}
        for a, x in result.items():
            for b, y in polynomial.items():
                z = shifted(a, b)
                updated[z] = updated.get(z, 0)+x*y
        result = {z: a for z, a in updated.items() if a}
    return result


def serialize(polynomial):
    return [[*z, a] for z, a in sorted(polynomial.items())]


def fixture_inputs(name):
    # Fixed mathematical inputs, not stored expected bounds or pattern answers.
    if name in ('three-line', 'higher-order'):
        normals = [(0, 1), (-2, 1), (-4, 1)]
        directions = [(1, 0), (1, 2), (1, 4)]
        offsets = [0, 1, 2]
        weights = ['one']*3
        coefficients = [[-1, 1], [-1, 1], [-1, 1]]
        if name == 'higher-order':
            weights = ['alternating-x', 'even-x', 'one']
            coefficients = [[1, 1], [-1, 0, 1], [-1, 1]]
        bg = 'zero'; extra = {(0, 0): 1}
    elif name == 'background':
        normals, directions, offsets = [(0, 1), (1, 0)], [(1, 0), (0, 1)], [0, 0]
        weights, coefficients = ['one', 'one'], [[-1, 1], [-1, 1]]
        bg = 'checkerboard'; extra = {(0, 0): 1, (1, 0): 1}
    else:
        raise ValueError('unknown configuration')
    lines = [{'normal': list(n), 'v': list(v), 'offset': a, 'weight': w}
             for n, v, a, w in zip(normals, directions, offsets, weights)]
    factors = [{(j*v[0], j*v[1]): a for j, a in enumerate(cs) if a}
               for v, cs in zip(directions, coefficients)]
    phi = sparse_product(factors); f = sparse_product([phi, extra])
    config = {'id': name, 'lines': lines, 'coefficients': coefficients, 'background': bg,
              'phase_modulus': 1 if name == 'three-line' else 2,
              'phi': serialize(phi), 'f': serialize(f), 'extra': serialize(extra)}
    return config, factors, phi, extra


def window(spec):
    if spec['kind'] == 'rectangle':
        return [(x, y) for x in range(spec['a']) for y in range(spec['b'])]
    if spec['kind'] == 'triangle':
        return [(x, y) for x in range(spec['n']+1) for y in range(spec['n']-x+1)]
    if spec['kind'] == 'point':
        return [(0, 0)]
    if spec['kind'] == 'segment':
        return [(j, 2*j) for j in range(spec['n']+1)]
    raise ValueError('unknown window')


def scalar_weight(line, x):
    return {'one': lambda: 1, 'alternating-x': lambda: 1 if x % 2 == 0 else -1,
            'even-x': lambda: int(x % 2 == 0)}[line['weight']]()


def pixels(S, config, anchor):
    values = []
    for s in S:
        z = shifted(s, anchor)
        a = (1 if (z[0]+z[1]) % 2 == 0 else -1) if config['background'] == 'checkerboard' else 0
        a += sum(scalar_weight(l, z[0]) for l in config['lines'] if inner(l['normal'], z) == l['offset'])
        values.append(a)
    return tuple(values)


def extended_gcd(a, b):
    old_r, r, old_x, x, old_y, y = a, b, 1, 0, 0, 1
    while r:
        q = old_r//r
        old_r, r = r, old_r-q*r
        old_x, x = x, old_x-q*x
        old_y, y = y, old_y-q*y
    return (old_x, old_y) if old_r == 1 else (-old_x, -old_y)


def pair_solution(n, a, m, b):
    z = legacy.solve_two(n, a, m, b)
    return legacy.integer_point(z)


def reconstruct_patterns(S, config):
    """Symbolic strata for zero/single hits; raw pixels at all pair intersections."""
    lines, L = config['lines'], config['phase_modulus']
    Q = [sorted(set(inner(l['normal'], s) for s in S)) for l in lines]
    patterns = set()
    # Each phase has an anchor off the finitely many event lines.
    for rx, ry in product(range(L), repeat=2):
        patterns.add(tuple((1 if (rx+ry+x+y) % 2 == 0 else -1)
                           if config['background'] == 'checkerboard' else 0 for x, y in S))
    for l, ts in zip(lines, Q):
        bx, by = extended_gcd(*l['normal'])
        check(inner(l['normal'], (bx, by)) == 1, 'normal is not primitive')
        for t in ts:
            base = ((l['offset']-t)*bx, (l['offset']-t)*by)
            for r in range(L):
                z = shifted(base, (r*l['v'][0], r*l['v'][1]))
                vals = []
                for s in S:
                    value = (1 if sum(shifted(s, z)) % 2 == 0 else -1) if config['background'] == 'checkerboard' else 0
                    if inner(l['normal'], s) == t:
                        value += scalar_weight(l, s[0]+z[0])
                    vals.append(value)
                patterns.add(tuple(vals))
    pair_anchors = set()
    for i, j in combinations(range(len(lines)), 2):
        for qi in Q[i]:
            for qj in Q[j]:
                z = pair_solution(lines[i]['normal'], lines[i]['offset']-qi,
                                  lines[j]['normal'], lines[j]['offset']-qj)
                if z is not None:
                    pair_anchors.add(z)
    for z in pair_anchors:
        patterns.add(pixels(S, config, z))
    event_count = L*L+L*sum(map(len, Q))+len(pair_anchors)
    return patterns, Q, pair_anchors, event_count


def reconstruct_sections(S, config, factors, phi, extra):
    SS = set(S); answers = []
    for i, line in enumerate(config['lines']):
        g = sparse_product([p for j, p in enumerate(factors) if j != i]+[extra])
        # Bounding-box intersection, independent of the producer's reference-point candidates.
        lx = max(min(x for x, y in S)-a for a, b in g)
        ux = min(max(x for x, y in S)-a for a, b in g)
        ly = max(min(y for x, y in S)-b for a, b in g)
        uy = min(max(y for x, y in S)-b for a, b in g)
        E = [z for z in product(range(lx, ux+1), range(ly, uy+1)) if all(shifted(z, q) in SS for q in g)]
        v = tuple(line['v']); transverse = lambda z: v[0]*z[1]-v[1]*z[0]
        C, CE = defaultdict(list), defaultdict(list)
        for s in S:
            C[transverse(s)].append(s)
        for s in E:
            CE[transverse(s)].append(s)
        # Check recurrence determinacy requires contiguous fibers, not just their size.
        for group in list(C.values())+list(CE.values()):
            ordered = sorted(group, key=lambda z: inner(v, z))
            check(all(shifted(a, v) == b for a, b in zip(ordered, ordered[1:])), 'nonconsecutive convex fiber')
        width = max(map(transverse, phi))-min(map(transverse, phi))
        degree = len(config['coefficients'][i])-1
        epsilon = int(sum(config['coefficients'][i]) == 0)
        K = sum(len(xs) >= degree for xs in CE.values())
        ell = 0
        for start in range(min(C)-width+1, max(C)+1):
            lengths = [len(C.get(t, [])) for t in range(start, start+width)]
            ell = max(ell, min(lengths))
        answers.append({'direction': list(v), 'g': serialize(g), 'E': [list(z) for z in sorted(E)],
                        'd': degree, 'epsilon': epsilon, 'w': width, 'K': K, 'ell': ell,
                        'bound': (K+epsilon)*(ell+1)})
    return answers


def annihilation_identities(config, f):
    # Every translated support-layer coefficient vanishes, for all residue phases.
    L = config['phase_modulus']
    for line in config['lines']:
        for rx, ry in product(range(L), repeat=2):
            groups = defaultdict(int)
            for shift, coefficient in f.items():
                groups[inner(line['normal'], shift)] += coefficient*scalar_weight(line, rx+shift[0])
            check(not any(groups.values()), 'filter does not annihilate a line globally')
    if config['background'] == 'checkerboard':
        check(sum(a*((-1)**((x+y) % 2)) for (x, y), a in f.items()) == 0,
              'filter does not annihilate the nonzero background')


def rebuild(name, spec):
    config, factors, phi, extra = fixture_inputs(name); S = window(spec)
    annihilation_identities(config, sparse_product([phi, extra]))
    sections = reconstruct_sections(S, config, factors, phi, extra)
    patterns, Q, pairs, events = reconstruct_patterns(S, config)
    return {'configuration': config, 'window': spec, 'sections': sections,
            'pattern_count': len(patterns), 'event_count': events, 'projection_counts': list(map(len, Q)),
            '_S': S, '_patterns': patterns, '_Q': Q, '_pairs': pairs, '_phi': phi}


def verify_summary(data, rebuilt):
    for key in ['configuration', 'window', 'sections', 'pattern_count', 'event_count', 'projection_counts']:
        check(data[key] == rebuilt[key], key+' mathematical reconstruction mismatch')
    for row in rebuilt['sections']:
        check(row['bound'] <= rebuilt['pattern_count'], 'section bound exceeds exact global patterns')


def verify_triangle(data, rebuilt):
    verify_summary(data, rebuilt)
    S = rebuilt['_S']; SS = set(S); config = rebuilt['configuration']; A = rebuilt['_phi']
    check(data['points'] == [list(s) for s in S], 'window points mismatch')
    polygon = legacy.hull(S)
    RZ = sorted(z for z in S if all(legacy.inside(shifted(z, a), polygon) for a in legacy.hull(A)))
    Td = [s for s in S if shifted(s, (1, 1)) in SS]
    check(data['RZ'] == [list(z) for z in RZ], 'RZ reconstruction mismatch')
    check(data['Td'] == [list(z) for z in Td], 'Td reconstruction mismatch')
    quad = len(S)+1-len(RZ)+len(Td)
    check(data['quad'] == quad and data['analytic_rank'] ==
          {'affine': len(S)+1-len(RZ), 'extended': quad,
           'type': 'analytic proof plus exact geometry; no large numerical minor'}, 'analytic rank metadata mismatch')
    cross = defaultdict(int)
    for i, j in product(range(3), repeat=2):
        if i != j:
            a, b = config['lines'][i], config['lines'][j]
            z = pair_solution(a['normal'], a['offset'], b['normal'], b['offset']-inner(b['normal'], (1, 1)))
            if z is not None:
                cross[z] += 1
    J = dict(cross)
    for v in [(1, 0), (1, 2), (1, 4)]:
        difference = defaultdict(int)
        for z, value in J.items():
            difference[z[0]-v[0], z[1]-v[1]] += value
            difference[z] -= value
        J = {z: a for z, a in difference.items() if a}
    check(data['cross'] == serialize(cross) and data['J'] == serialize(J), 'complete witness reconstruction mismatch')
    check(J.get((-5, -9)) == 1, 'genuine nonzero witness missing')
    # All potential support points receive a direct pixel check.
    for z in {tuple(p-q for p, q in zip(a, b)) for a in cross for b in A}:
        value = sum(coefficient*pixels([(0, 0)], config, shifted(z, q))[0]*
                    pixels([(1, 1)], config, shifted(z, q))[0] for q, coefficient in A.items())
        check(value == J.get(z, 0), 'witness raw pixel check failed')
    # Reconstruct all coverage keys and check avoidance/phase conditions mathematically.
    Q = rebuilt['_Q']; pairs = rebuilt['_pairs']; seen = set()
    expected = {('zero', 0, 0)} | {('single', i, t, 0) for i, ts in enumerate(Q) for t in ts}
    expected |= {('multiple', *z) for z in pairs}
    for event in data['events']:
        z = tuple(event['anchor'])
        hits = [i for i, l in enumerate(config['lines']) if l['offset']-inner(l['normal'], z) in Q[i]]
        kind = event['kind']
        if kind == 'zero':
            key = ('zero', *event['phase'])
            # The producer's first transverse direction is (1,1) for these inputs.
            check(event['phase'] == [0, 0] and z == (event['avoid_step'], event['avoid_step'])
                  and event['avoid_step'] >= 0 and hits == [], 'zero representative collision')
        elif kind == 'single':
            i, t, phase = event['line'], event['offset'], event['phase']
            key = ('single', i, t, phase)
            l = config['lines'][i]
            # Its primitive-normal Bezout origin is (0, i-t), including negative x coefficients.
            check(hits == [i] and l['offset']-inner(l['normal'], z) == t and phase == 0
                  and z == (event['avoid_step'], i-t+2*i*event['avoid_step'])
                  and event['avoid_step'] >= 0, 'single representative collision or phase mismatch')
        else:
            key = ('multiple', *z)
            check(kind == 'multiple' and z in pairs and len(hits) >= 2, 'invalid multiple-hit anchor')
        check(key in expected and key not in seen, 'invalid or duplicate coverage event')
        seen.add(key)
    check(seen == expected, 'global coverage event omission')
    check(data['multiple_anchor_count'] == len(pairs), 'multiple anchor count mismatch')
    masks = sorted(sum(value << j for j, value in enumerate(p)) for p in rebuilt['_patterns'])
    check([row['hex'] for row in data['patterns']] == [hex(m) for m in masks], 'full global pattern set mismatch')
    for row in data['patterns']:
        p = pixels(S, config, row['anchor'])
        check(sum(value << j for j, value in enumerate(p)) == int(row['hex'], 16), 'pattern representative pixel mismatch')
    width = (len(S)+7)//8
    digest = sha256(b''.join(m.to_bytes(width, 'little') for m in masks)).hexdigest()
    check(data['byte_width'] == width and data['pattern_sha256'] == digest, 'pattern fingerprint mismatch')
    return {'T': len(S)+1, 'quad': quad, 'SC': max(s['bound'] for s in rebuilt['sections']),
            'actual_patterns': len(masks), 'fingerprint': digest, 'multiple_anchors': len(pairs),
            'events': len(expected), 'witness_points': len(J), 'analytic_rank': data['analytic_rank']}


def negative_controls(data, rebuilt):
    tests = []
    def add(name, mutate, expected):
        damaged = copy.deepcopy(data); mutate(damaged)
        try:
            verify_triangle(damaged, rebuilt)
        except ValueError as error:
            check(expected in str(error), 'negative rejected for wrong reason: '+str(error))
            tests.append({'name': name, 'rejected': True, 'mathematical_reason': str(error)})
        else:
            raise ValueError('tampering escaped: '+name)
    add('section K', lambda d: d['sections'][2].__setitem__('K', 126), 'sections mathematical')
    add('stripe ell', lambda d: d['sections'][2].__setitem__('ell', 7), 'sections mathematical')
    add('conditional epsilon', lambda d: d['sections'][2].__setitem__('epsilon', 0), 'sections mathematical')
    add('erosion omission', lambda d: d['sections'][2]['E'].pop(), 'sections mathematical')
    add('witness coefficient', lambda d: d['J'][0].__setitem__(2, d['J'][0][2]+1), 'witness reconstruction')
    add('coverage omission', lambda d: d['events'].pop(), 'coverage event omission')
    add('single collision', lambda d: d['events'][1].__setitem__('anchor', [0, 0]), 'single representative')
    def remove_pattern(d):
        d['patterns'].pop()
        width = d['byte_width']
        d['pattern_sha256'] = sha256(b''.join(int(p['hex'], 16).to_bytes(width, 'little') for p in d['patterns'])).hexdigest()
    add('pattern omission with updated digest', remove_pattern, 'global pattern set mismatch')
    add('fake 679 minor status', lambda d: d['analytic_rank'].__setitem__('type', 'numerical minor verified'), 'rank metadata')
    return tests


def main():
    triangle = json.loads((ROOT/'证据/三角形全局证据-v1.0.json').read_text())
    reference = rebuild('three-line', {'kind': 'triangle', 'n': 30})
    result = verify_triangle(triangle, reference)
    controls = negative_controls(triangle, reference)
    test_data = json.loads((ROOT/'证据/比较与压力测试-v1.0.json').read_text())
    expected_specs = [('higher-order', {'kind': 'rectangle', 'a': a, 'b': b}) for a in range(1, 9) for b in range(1, 9)]
    expected_specs += [('higher-order', {'kind': 'triangle', 'n': n}) for n in range(21)]
    expected_specs += [('background', {'kind': 'rectangle', 'a': 6, 'b': 9}),
                       ('higher-order', {'kind': 'point'}), ('higher-order', {'kind': 'segment', 'n': 6})]
    check(len(test_data['stress']) == len(expected_specs), 'stress coverage incomplete')
    stress_results = []
    for record, (name, spec) in zip(test_data['stress'], expected_specs):
        rebuilt = rebuild(name, spec); verify_summary(record, rebuilt)
        stress_results.append({'configuration': name, 'window': spec, 'patterns': rebuilt['pattern_count'],
                               'bounds': [s['bound'] for s in rebuilt['sections']]})
    # Must reject the two particularly tempting pressure-test corruptions.
    for idx, field, value in [(0, 'epsilon', 1), (64, 'ell', 1)]:
        damaged = copy.deepcopy(test_data['stress'][idx]); damaged['sections'][0][field] = value
        rebuilt = rebuild(damaged['configuration']['id'], damaged['window'])
        try:
            verify_summary(damaged, rebuilt)
        except ValueError as e:
            check('sections mathematical' in str(e), 'unexpected stress rejection')
            controls.append({'name': 'stress '+field, 'rejected': True, 'mathematical_reason': str(e)})
        else:
            raise ValueError('stress mutation escaped')
    comparisons = []
    comparison_specs = [{'kind': 'rectangle', 'a': 6, 'b': 9}, {'kind': 'rectangle', 'a': 30, 'b': 30},
                        {'kind': 'triangle', 'n': 1}, {'kind': 'triangle', 'n': 20}, {'kind': 'triangle', 'n': 50}]
    check(len(test_data['comparisons']) == len(comparison_specs), 'comparison coverage incomplete')
    for record, spec in zip(test_data['comparisons'], comparison_specs):
        rebuilt = rebuild('three-line', spec); verify_summary(record, rebuilt)
        comparisons.append({'window': spec, 'patterns': rebuilt['pattern_count'],
                            'SC': max(s['bound'] for s in rebuilt['sections'])})
    legacy_results = []
    certs = []
    for name in legacy.CERT_NAMES:
        cert = json.loads((ROOT/'证据/复用'/name).read_text()); certs.append(cert)
        legacy_results.append(legacy.check_certificate(cert))
    old_controls = legacy.negative_controls(certs[1])
    report = {'passed': True, 'independence': 'Separate producer/checker implementations; same Codex context; legacy checker reused.',
              'triangle': result, 'comparisons': comparisons, 'stress_windows': len(stress_results),
              'stress_direction_checks': sum(len(row['bounds']) for row in stress_results),
              'stress': stress_results, 'new_negative_controls': controls,
              'legacy_results': legacy_results, 'legacy_negative_controls': old_controls,
              'review': {'model': 'gpt-6.1-sol', 'fresh_context': True, 'mathematical_blockers': 0, 'record': '对抗复核-v1.0.md', 'reviewed_manuscript_sha256': '3bd81a166c53f8a073ad893eeaef24fe05b83468023151b3b550db385d9fd52c'},
              'scope': 'Stress cases verify general SC nonzero-background handling; Case B parameter bridge and general theorem are proved in manuscript, not by finite tests'}
    (ROOT/'运行记录/独立重建检查结果-v1.0.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'passed': True, 'triangle': result, 'stress_windows': len(stress_results),
                      'new_negative_controls_rejected': len(controls), 'legacy_negative_controls_rejected': len(old_controls)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
