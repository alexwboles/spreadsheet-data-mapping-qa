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
native checks. The existing installer must be rebuilt to include readable
notices before it is considered for distribution. Clean-machine acceptance and
Alex's specific distribution approval remain required.

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
native acceptance result to this binary. Full pass/stale/error regression,
installer notice inclusion and clean Windows machine testing remain pending.
No installed product was replaced or download published.
