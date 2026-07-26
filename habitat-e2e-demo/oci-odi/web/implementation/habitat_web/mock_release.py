from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import tarfile
from pathlib import Path


def _release_files(implementation_root: Path) -> list[tuple[Path, str, int]]:
    package_files = (
        "__init__.py",
        "mock_api.py",
        "mock_server.py",
        "pipeline.py",
        "transformations.py",
    )
    files = [
        (path, f"habitat-web-mock/habitat_web/{path.name}", 0o644)
        for path in (
            implementation_root / "habitat_web" / name
            for name in package_files
        )
    ]
    files.extend(
        (
            path,
            f"habitat-web-mock/fixtures/{path.name}",
            0o644,
        )
        for path in sorted(
            (
                implementation_root / "fixtures" / "mock-responses"
            ).glob("*.json")
        )
    )
    files.append(
        (
            implementation_root / "start-mock-backend.sh",
            "habitat-web-mock/start-mock-backend.sh",
            0o755,
        )
    )
    if any(not source.is_file() for source, _, _ in files):
        raise FileNotFoundError("mock release source is incomplete")
    return files


def build_release(implementation_root: Path, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=buffer, mtime=0
    ) as compressed:
        with tarfile.open(
            fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT
        ) as archive:
            for source, archive_name, mode in _release_files(
                implementation_root
            ):
                content = source.read_bytes()
                info = tarfile.TarInfo(archive_name)
                info.size = len(content)
                info.mode = mode
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = "root"
                info.gname = "root"
                archive.addfile(info, io.BytesIO(content))
    payload = buffer.getvalue()
    output.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(build_release(args.implementation_root, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
