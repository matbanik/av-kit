"""E2E_ASSERTION_CENSUS_RULE census generator (AC-45.20, MOUNT_COMPLETENESS_RULE clause 8).

Emits, per E2E queue spec and per test case, the expect() count and the capability each
assertion covers. Capability is resolved from the RETIRED_TOOLBAR_CONTROLS per-page
sub-map plus a small set of page-level capabilities, so the after-census can be compared
capability-for-capability, not merely count-for-count.

    python e2e-assertion-census.py <out-file> [repo-root]

<repo-root> defaults to this file's repository. `assert-mount-completeness.ps1`
-SelfTest passes a fixture tree instead, so the gate's self-test reuses this
attribution logic rather than duplicating it.

The rule: after the rewrite, no capability line may fall to zero assertions and the total
assertion count may not fall. Run once BEFORE the first rewrite (task row 2) and again at
each gate; `assert-mount-completeness.ps1` clause 8 compares the two receipts.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SETS = os.path.join(HERE, 'named-sets.json')
FILES = [
    ('converter', os.path.join(REPO, 'ui', 'tests', 'e2e', 'convert-queue.test.ts')),
    ('downloader', os.path.join(REPO, 'ui', 'tests', 'e2e', 'download-queue.test.ts')),
]

# Page-level capabilities that are not retired toolbar controls but must keep assertions
# across the rewrite. Ids that do not exist yet simply report zero and are informational;
# the binding floor is the retired-control table plus the total count.
PAGE_CAPABILITIES = {
    'converter': {
        'convert-page': 'converter page mounts',
        'convert-dropzone': 'staging drop zone present',
        'convert-browse': 'staging Browse picker',
        'convert-add': 'add to queue',
        'convert-queue': 'queue surface renders',
        'convert-queue-row': 'queue row renders',
        'convert-queue-summary': 'queue summary',
        'convert-processor': 'processor indicator',
        'queue-toolbar': 'queue toolbar',
        'queue-empty-dropzone': 'empty-queue drop invitation',
        'queue-empty-browse': 'empty-queue Browse',
        'queue-drop-strip': 'non-empty drop strip',
    },
    'downloader': {
        'downloader-page': 'downloader page mounts',
        'url-input': 'URL intake field',
        'add-btn': 'add to queue',
        'queue-table': 'legacy queue surface',
        'queue-row': 'legacy queue row',
        'queue-list': 'queue surface renders',
        'queue-card': 'queue card renders',
        'queue-summary': 'queue summary',
        'processor-indicator': 'processor indicator',
        'queue-toolbar': 'queue toolbar',
        'queue-empty-invite': 'empty-queue URL invitation',
        'queue-empty-invite-action': 'empty-queue invitation action',
    },
}

TEST_RE = re.compile(r"^\s*test\(\s*['\"](?P<title>[^'\"]+)['\"]")
TESTID_RE = re.compile(
    r"""getByTestId\(\s*['"]([a-z0-9:-]+)['"]|data-testid=\\?["']([a-z0-9:-]+)\\?["']"""
)


def census(page, path, retired):
    src = io.open(path, encoding='utf-8').read().split('\n')
    ids = set(retired.get(page, {}))
    page_caps = PAGE_CAPABILITIES[page]

    cases = []
    cur = None
    for line in src:
        m = TEST_RE.match(line)
        if m:
            cur = {'title': m.group('title'), 'expects': 0, 'caps': {}}
            cases.append(cur)
        if cur is None:
            continue
        n = line.count('expect(')
        cur['expects'] += n
        # An assertion and the locator it wraps are usually the same line; when the
        # locator sits on its own line the assertion that follows still lands in the
        # same case, which is the unit the rule compares.
        for a, b in TESTID_RE.findall(line):
            tid = a or b
            if tid in ids:
                key = 'retired:' + tid
            elif tid in page_caps:
                key = 'page:%s (%s)' % (tid, page_caps[tid])
            else:
                continue
            cur['caps'][key] = cur['caps'].get(key, 0) + n
    return cases


def main():
    global REPO, FILES
    if len(sys.argv) not in (2, 3):
        sys.stderr.write('usage: e2e-assertion-census.py <out-file> [repo-root]\n')
        return 2
    out_path = sys.argv[1]
    if len(sys.argv) == 3:
        REPO = os.path.abspath(sys.argv[2])
        FILES = [
            ('converter', os.path.join(REPO, 'ui', 'tests', 'e2e', 'convert-queue.test.ts')),
            ('downloader', os.path.join(REPO, 'ui', 'tests', 'e2e', 'download-queue.test.ts')),
        ]
    sets = json.load(io.open(SETS, encoding='utf-8'))
    retired = sets['RETIRED_TOOLBAR_CONTROLS']['value']

    lines = []
    lines.append('E2E ASSERTION CENSUS')
    lines.append('rule: E2E_ASSERTION_CENSUS_RULE (AC-45.20, MOUNT_COMPLETENESS_RULE clause 8)')
    lines.append('generator: docs/execution/plans/2026-09-02-p10-queue-card-migration/'
                 'e2e-assertion-census.py')
    lines.append('=' * 78)

    grand_expects = 0
    grand_cases = 0
    for page, path in FILES:
        if not os.path.exists(path):
            sys.stderr.write('missing spec: %s\n' % path)
            return 1
        cases = census(page, path, retired)
        total = sum(c['expects'] for c in cases)
        grand_expects += total
        grand_cases += len(cases)
        rel = os.path.relpath(path, REPO).replace('\\', '/')
        lines.append('')
        lines.append('FILE %s  [page=%s]' % (rel, page))
        lines.append('  test cases: %d   expect() assertions: %d' % (len(cases), total))
        lines.append('  ' + '-' * 74)
        for c in cases:
            lines.append('  %-70s %3d' % (c['title'][:70], c['expects']))
            for cap in sorted(c['caps']):
                lines.append('        capability %-56s %3d' % (cap[:56], c['caps'][cap]))

        covered = {}
        for c in cases:
            for cap, n in c['caps'].items():
                if cap.startswith('retired:'):
                    covered[cap[8:]] = covered.get(cap[8:], 0) + n
        lines.append('  ' + '-' * 74)
        lines.append('  RETIRED-CONTROL COVERAGE (%s sub-map of RETIRED_TOOLBAR_CONTROLS)' % page)
        for tid in sorted(retired[page]):
            homes = '; '.join('%s [%s]' % (h['home'], h['meu']) for h in retired[page][tid])
            lines.append('    %-18s assertions=%-3d homes: %s'
                         % (tid, covered.get(tid, 0), homes))

    lines.append('')
    lines.append('=' * 78)
    lines.append('TOTAL test cases in the two queue specs: %d' % grand_cases)
    lines.append('TOTAL expect() assertions in the two queue specs: %d' % grand_expects)
    lines.append('')
    lines.append('AFTER-CENSUS CONTRACT: no capability line above may fall to zero assertions,')
    lines.append('and the TOTAL assertion count may not fall below %d.' % grand_expects)

    io.open(out_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    sys.stdout.write('\n'.join(lines) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
