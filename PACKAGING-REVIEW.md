# Isolated Windows package review

## Scope and requirements

The November 2 PyInstaller inventory resolved Windows runtime DLLs from an
unrelated tool's directory on PATH. Build review artifacts using only the
explicit CPython runtime and Windows paths; reject other binary origins.
Preserve dependency notices, verify their hashes inside the executable, include
readable copies and an artifact inventory. Never replace an installed app,
download build dependencies or publish a release from this command.

## Build and acceptance

Run `py -3.11 build_review.py` with the existing CPython 3.11.9 and PyInstaller
6.22.3. Each run creates a new ignored build/isolated-review-* directory. The
command fails if tool versions, notice hashes, binary origins or embedded
notice hashes do not match. Read build.log if a build fails. This checks
traceability; repeat the actual native workflow on a new executable before
accepting it. Tests on one development PC do not prove clean-machine support.

## Deployment and maintenance

Output is an unsigned local review folder, not a published release or installer.
Existing installed software and previous review packages remain available.
Updating runtimes requires reviewing their notices and repeating package and
native checks. Installer source explicitly includes the five notices, their
provenance manifest and README. Uninstall removes only these known files and
leaves unrelated files in that directory intact. Rebuild an actual installer
from an accepted application artifact before considering distribution;
clean-machine acceptance and Alex's specific distribution approval remain required.

## November 3 result

Existing tools built a new unsigned local executable at
build/isolated-review-njtaxge3/package. SHA256:
943b394b95419a0d236e2528e8d80ecf38828e3872508e9d94b368d058b41285.
All 13 BINARY/EXTENSION entries came from the selected CPython distribution;
none came from the unrelated runtime folder. Five embedded notice hashes were
verified against the saved unaltered source texts. The readable copies and
build inventory are adjacent to the executable.

The new executable launched and displayed the known defective synthetic audit.
Native Save As created parseable JSON with counts 4/5, passed:false and both
swapped fields for ID1002. This smoke check does not transfer every earlier
native acceptance result to this binary. The additional native checks below
now cover passing output, stale-input refusal and malformed-map recovery.
An actual application installer and clean Windows machine testing remain pending.
No installed product was replaced or download published.

Installer notice inclusion was then verified using existing NSIS 3.13 and a
non-executable synthetic payload in an isolated QA directory. All seven readable
notice/provenance files matched their source bytes; the five license hashes
also matched the saved manifest. Upgrade retained an unrelated customer-note
fixture. Uninstall removed only the seven owned notice files and kept that note
and an unrelated report. All 31 source/installer tests passed. These checks do
not validate a customer application installer or establish release readiness.

## Isolated executable follow-through

The same unsigned executable (SHA256 above) passed a four-record comparison
using copied synthetic CSVs and the agreed field map. Native Save As produced
a valid JSON report with all three input hashes verified. Changing the migrated
fixture at the same path then caused Save report to refuse the stale result,
clear the old output and create no stale report. After restoring the fixture,
a deliberately malformed map produced a failed-check message and could not be
saved. Restoring the map and running Check files returned a valid passing result.
All fixture bytes were restored and reverified; only the isolated app was closed.

These are observed workflows on this development PC. They do not establish
clean-machine installation, signed distribution or every possible native error
path. The raw JSON syntax error remains a usability improvement to consider;
it did not permit a false pass or a stale report.
