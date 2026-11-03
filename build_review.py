"""Build an isolated, unsigned Windows review package with existing tools only.

Does not download dependencies, install the app, sign it or publish a release.
Every invocation creates a new directory under ignored build/.
"""
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if os.name != "nt" or sys.version_info[:3] != (3, 11, 9):
        raise SystemExit("Use the reviewed Windows CPython 3.11.9 runtime.")
    version = importlib.metadata.version("pyinstaller")
    if version != "6.22.3":
        raise SystemExit("Use existing PyInstaller 6.22.3; no automatic installs.")
    notice_root = ROOT / "third-party"
    notice_manifest = json.loads((notice_root / "notice-sources.json").read_text())
    for item in notice_manifest["notices"]:
        if digest(notice_root / item["file"]) != item["sha256"]:
            raise SystemExit(f"Notice does not match reviewed source: {item['file']}")

    base = ROOT / "build"
    base.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="isolated-review-", dir=base)).resolve()
    if not work.is_relative_to(base.resolve()):
        raise SystemExit("Build output must stay inside build/.")
    package = work / "package"
    package.mkdir()
    python_root = Path(sys.base_prefix).resolve()
    windows_root = Path(os.environ["SystemRoot"]).resolve()
    env = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "TCL_LIBRARY", "TK_LIBRARY"):
        env.pop(key, None)
    # Prevent DLL resolution from unrelated tools on the interactive PATH.
    env["PATH"] = os.pathsep.join(map(str, (
        python_root, python_root / "DLLs", windows_root / "System32", windows_root,
    )))
    command = [
        sys.executable, "-I", "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onefile", "--windowed", "--noupx",
        "--name", "TechPartner-Spreadsheet-Check-Review",
        "--distpath", str(package), "--workpath", str(work / "work"),
        "--specpath", str(work / "spec"),
        "--add-data", f"{notice_root}{os.pathsep}third-party",
        str(ROOT / "desktop.py"),
    ]
    with (work / "build.log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                                stderr=subprocess.STDOUT, timeout=300)
    if result.returncode:
        raise SystemExit(f"Build failed; see {work / 'build.log'}")
    toc_path = work / "work" / "TechPartner-Spreadsheet-Check-Review" / "PKG-00.toc"
    toc = ast.literal_eval(toc_path.read_text(encoding="utf-8"))
    inventory = []
    for name, source, kind in toc[2]:
        if kind not in ("BINARY", "EXTENSION"):
            continue
        path = Path(source).resolve()
        if path.is_relative_to(python_root):
            origin = "CPython/" + path.relative_to(python_root).as_posix()
        elif path.is_relative_to(windows_root):
            origin = "Windows/" + path.relative_to(windows_root).as_posix()
        else:
            raise SystemExit(f"Unreviewed binary origin: {name}; package is not accepted.")
        inventory.append({"file": name, "origin": origin, "sha256": digest(path)})
    shutil.copytree(notice_root, package / "third-party")
    shutil.copyfile(ROOT / "USER-GUIDE.txt", package / "USER-GUIDE.txt")
    exe = package / "TechPartner-Spreadsheet-Check-Review.exe"
    # Verify the notices actually entered the one-file archive, not just a folder.
    from PyInstaller.archive.readers import CArchiveReader
    archive = CArchiveReader(str(exe))
    for item in notice_manifest["notices"]:
        key = "third-party\\" + item["file"]
        if hashlib.sha256(archive.extract(key)).hexdigest() != item["sha256"]:
            raise SystemExit(f"Embedded notice mismatch: {key}")
    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "unsigned local review; not a commercial release",
        "python": sys.version.split()[0], "pyinstaller": version,
        "binary_inventory": inventory,
        "package_files": [
            {"file": p.relative_to(package).as_posix(), "sha256": digest(p)}
            for p in sorted(package.rglob("*")) if p.is_file()
        ],
    }
    (package / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"package": str(package), "sha256": digest(exe),
                      "binary_count": len(inventory), "embedded_notices": len(notice_manifest["notices"])}))


if __name__ == "__main__":
    main()
