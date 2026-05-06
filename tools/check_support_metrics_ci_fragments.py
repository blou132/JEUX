from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExpectedFragmentFile:
    file_name: str
    category: str


EXPECTED_FRAGMENT_FILES: tuple[ExpectedFragmentFile, ...] = (
    ExpectedFragmentFile("health_summary_expected_fragments.txt", "health"),
    ExpectedFragmentFile("health_report_expected_fragments.txt", "health"),
    ExpectedFragmentFile("smoke_summary_expected_fragments.txt", "smoke"),
    ExpectedFragmentFile("smoke_report_expected_fragments.txt", "smoke"),
    ExpectedFragmentFile("runtime_skip_summary_expected_fragments.txt", "runtime"),
    ExpectedFragmentFile("runtime_skip_report_expected_fragments.txt", "runtime"),
    ExpectedFragmentFile("error_summary_expected_fragments.txt", "error"),
    ExpectedFragmentFile("error_report_expected_fragments.txt", "error"),
    ExpectedFragmentFile("local_simulation_summary_expected_fragments.txt", "local"),
    ExpectedFragmentFile("local_simulation_report_expected_fragments.txt", "local"),
)
EXPECTED_CATEGORIES: tuple[str, ...] = (
    "health",
    "smoke",
    "runtime",
    "error",
    "local",
)


@dataclass
class FragmentFileStatus:
    file_name: str
    category: str
    path: Path
    exists: bool
    fragment_count: int
    status: str


@dataclass
class FragmentValidationResult:
    directory: Path
    files: list[FragmentFileStatus]
    missing_files: list[str]
    empty_files: list[str]
    unreadable_files: list[str]
    missing_categories: list[str]
    issues: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check support metrics CI output fragment files used by readability "
            "snapshot tests."
        )
    )
    parser.add_argument(
        "--fragments-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "tests"
        / "fixtures"
        / "support_metrics_ci_outputs",
        help="Directory containing support metrics CI fragment snapshot files.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List fragment files with category and loaded fragment count.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Return non-zero when required fragment files are missing/invalid.",
    )
    parser.add_argument(
        "--print-missing",
        action="store_true",
        help="Print the list of missing required fragment files.",
    )
    return parser


def _load_fragment_count(path: Path) -> tuple[int, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return 0, str(exc)

    count = 0
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line == "" or line.startswith("#"):
            continue
        count += 1
    return count, ""


def inspect_fragment_directory(fragments_dir: Path) -> FragmentValidationResult:
    files: list[FragmentFileStatus] = []
    missing_files: list[str] = []
    empty_files: list[str] = []
    unreadable_files: list[str] = []
    issues: list[str] = []
    category_has_non_empty_file: dict[str, bool] = {
        category: False for category in EXPECTED_CATEGORIES
    }

    for expected_file in EXPECTED_FRAGMENT_FILES:
        path = fragments_dir / expected_file.file_name
        if not path.exists():
            files.append(
                FragmentFileStatus(
                    file_name=expected_file.file_name,
                    category=expected_file.category,
                    path=path,
                    exists=False,
                    fragment_count=0,
                    status="missing",
                )
            )
            missing_files.append(expected_file.file_name)
            issues.append("missing fragment file: %s" % expected_file.file_name)
            continue

        fragment_count, read_error = _load_fragment_count(path)
        if read_error:
            files.append(
                FragmentFileStatus(
                    file_name=expected_file.file_name,
                    category=expected_file.category,
                    path=path,
                    exists=True,
                    fragment_count=0,
                    status="unreadable",
                )
            )
            unreadable_files.append(expected_file.file_name)
            issues.append(
                "unreadable fragment file: %s (%s)"
                % (expected_file.file_name, read_error)
            )
            continue

        if fragment_count <= 0:
            files.append(
                FragmentFileStatus(
                    file_name=expected_file.file_name,
                    category=expected_file.category,
                    path=path,
                    exists=True,
                    fragment_count=0,
                    status="empty",
                )
            )
            empty_files.append(expected_file.file_name)
            issues.append(
                "empty fragment file (no non-comment fragments): %s"
                % expected_file.file_name
            )
            continue

        files.append(
            FragmentFileStatus(
                file_name=expected_file.file_name,
                category=expected_file.category,
                path=path,
                exists=True,
                fragment_count=fragment_count,
                status="ok",
            )
        )
        category_has_non_empty_file[expected_file.category] = True

    missing_categories = [
        category
        for category, present in category_has_non_empty_file.items()
        if not present
    ]
    for category in missing_categories:
        issues.append("missing fragment category coverage: %s" % category)

    return FragmentValidationResult(
        directory=fragments_dir,
        files=files,
        missing_files=missing_files,
        empty_files=empty_files,
        unreadable_files=unreadable_files,
        missing_categories=missing_categories,
        issues=issues,
    )


def _print_summary(result: FragmentValidationResult) -> None:
    expected_count = len(EXPECTED_FRAGMENT_FILES)
    present_count = len([file for file in result.files if file.exists])
    ok_count = len([file for file in result.files if file.status == "ok"])
    covered_categories = sorted(
        {
            file.category
            for file in result.files
            if file.status == "ok"
        }
    )

    print("Support metrics CI fragments maintenance")
    print("- directory: %s" % result.directory)
    print("- expected files: %d" % expected_count)
    print("- present files: %d/%d" % (present_count, expected_count))
    print("- non-empty files: %d/%d" % (ok_count, expected_count))
    print(
        "- categories with non-empty fragments: %s"
        % (", ".join(covered_categories) if covered_categories else "none")
    )
    if result.missing_categories:
        print("- missing categories: %s" % ", ".join(result.missing_categories))
    else:
        print("- missing categories: none")


def _print_list(result: FragmentValidationResult) -> None:
    print("")
    print("Fragments list")
    for file_status in result.files:
        print(
            "- %s | category=%s | fragments=%d | status=%s"
            % (
                file_status.file_name,
                file_status.category,
                file_status.fragment_count,
                file_status.status,
            )
        )


def _print_missing_files(result: FragmentValidationResult) -> None:
    print("")
    if result.missing_files:
        print("Missing files")
        for file_name in result.missing_files:
            print("- %s" % file_name)
    else:
        print("Missing files")
        print("- none")


def _print_issues(result: FragmentValidationResult) -> None:
    print("")
    if result.issues:
        print("Validation issues")
        for issue in result.issues:
            print("- %s" % issue)
    else:
        print("Validation issues")
        print("- none")


def main() -> int:
    args = _build_parser().parse_args()
    result = inspect_fragment_directory(args.fragments_dir)

    _print_summary(result)
    if args.list:
        _print_list(result)
    if args.print_missing:
        _print_missing_files(result)
    _print_issues(result)

    if args.validate:
        if result.is_valid:
            print("")
            print("Validation status: valid")
            return 0
        print("")
        print("Validation status: invalid")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
