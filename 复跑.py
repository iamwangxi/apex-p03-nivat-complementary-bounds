#!/usr/bin/env python3
"""Offline reconstruction and portable-package gate; no Git/network calls."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def package_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and '.git' not in p.relative_to(ROOT).parts
                  and '__pycache__' not in p.relative_to(ROOT).parts
                  and p.name not in ['MANIFEST.sha256', '.DS_Store'])


def manifest_check():
    rows = {}
    for line in (ROOT/'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert name not in rows and not Path(name).is_absolute() and '..' not in Path(name).parts
        rows[name] = digest
    actual = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in package_files()}
    assert rows == actual, 'manifest bytes or file inventory mismatch'
    return len(rows)


def manuscript_check():
    path = ROOT/'优化合稿-English-v1.1.md'; data = path.read_bytes(); text = data.decode('utf-8')
    units = len(text.encode('utf-16-le'))//2
    body = text.split('\n', 1)[1].strip('\n')
    assert (ROOT/'proof/submission.md').read_bytes() == body.encode('utf-8')
    assert len(body.encode('utf-16-le'))//2 <= 20000 and text.splitlines()[0].startswith('Complementary complexity bounds')
    tokens = list(re.finditer(r'(?<!\\)\$\$|(?<!\\)\$', text))
    opening = None; formulas = []
    for token in tokens:
        if opening is None:
            opening = token
        else:
            assert token.group() == opening.group(), 'mixed/unclosed formula delimiters'
            formula = text[opening.end():token.start()]
            braces = re.sub(r'\\[{}]', '', formula)
            depth = 0
            for c in braces:
                depth += (c == '{')-(c == '}')
                assert depth >= 0, 'unbalanced mathematical braces'
            assert depth == 0, 'unclosed mathematical brace'
            formulas.append(formula); opening = None
    assert opening is None, 'unclosed math delimiter'
    # Active local navigation links; archived reference documents retain historical links.
    for p in [ROOT/name for name in ['README.md', '引用与披露.md', '复跑说明.md', '证据协议-v1.0.md', path.name]]:
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' not in target:
                assert (p.parent/target.split('#')[0]).is_file(), 'unresolved local link: '+target
    return units, hashlib.sha256(data).hexdigest(), len(formulas)


def run(relative):
    subprocess.run([sys.executable, '-B', str(ROOT/relative)], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--regenerate', action='store_true')
    args = parser.parse_args()
    assert sys.version_info >= (3, 9), 'Python 3.9+ required'
    count = manifest_check(); units, digest, formulas = manuscript_check()
    if args.regenerate:
        old = {p: (ROOT/p).read_bytes() for p in ['证据/三角形全局证据-v1.0.json', '证据/比较与压力测试-v1.0.json']}
        run('生成器/生成证据.py')
        assert all((ROOT/p).read_bytes() == b for p, b in old.items()), 'producer not byte-reproducible'
    run('检查器/独立重建检查.py')
    run('检查器/障碍与无限族检查.py')
    assert manifest_check() == count
    print('PACKAGE PASS: files={}, UTF16={}, formulas={}, manuscript SHA256={}'.format(count, units, formulas, digest))


if __name__ == '__main__':
    main()
