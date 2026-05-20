import re
import sys
import argparse
import os


def parse_frontmatter(filepath):
    """Extract 'name' and 'description' from a markdown file's YAML frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print(f"ERROR: No YAML frontmatter found in '{filepath}'.", file=sys.stderr)
        sys.exit(1)

    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)

    if not name_match:
        print("ERROR: 'name' field not found in frontmatter.", file=sys.stderr)
        sys.exit(1)
    if not desc_match:
        print("ERROR: 'description' field not found in frontmatter.", file=sys.stderr)
        sys.exit(1)

    return name_match.group(1).strip(), desc_match.group(1).strip()


def validate_metadata(name, description, filepath=None):
    errors = []

    # 1. Validate Name Length
    if not (1 <= len(name) <= 64):
        errors.append(f"NAME ERROR: '{name}' is {len(name)} characters. Must be between 1-64.")

    # 2. Validate Name Characters (lowercase, numbers, single hyphens)
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(
            f"NAME ERROR: '{name}' contains invalid characters. "
            "Use only lowercase letters, numbers, and single hyphens. "
            "No consecutive hyphens, and cannot start/end with a hyphen."
        )

    # 3. Validate Name XML Tags
    if re.search(r"<[^>]+>", name):
        errors.append(
            "NAME ERROR: name contains XML tags ('<...>'). "
            "XML tags are not allowed in the name field."
        )

    # 4. Validate Name Reserved Words
    name_lower = name.lower()
    reserved_words = ["anthropic", "claude"]
    found_reserved = [w for w in reserved_words if w in name_lower]
    if found_reserved:
        errors.append(
            f"NAME ERROR: name contains reserved word(s): {found_reserved}. "
            "The name cannot contain 'anthropic' or 'claude'."
        )

    # 5. Validate Name Convention (Gerund Form Advisory)
    segments = name.split("-")
    has_gerund = any(seg.endswith("ing") for seg in segments)
    if not has_gerund:
        errors.append(
            "NAME ADVISORY: Consider using gerund form for the skill name "
            "(e.g., 'processing-pdfs') for clarity and consistency."
        )

    # 6. Validate Description Length
    if not description or not description.strip():
        errors.append("DESCRIPTION ERROR: Description is empty. It must be non-empty.")
    elif len(description) > 1024:
        errors.append(
            f"DESCRIPTION ERROR: Description is {len(description)} characters. "
            "Must be 1,024 characters or fewer."
        )

    # 7. Validate Description XML Tags
    if re.search(r"<[^>]+>", description):
        errors.append(
            "DESCRIPTION ERROR: description contains XML tags ('<...>'). "
            "XML tags are not allowed in the description field."
        )

    # 8. Check for Third-Person Perspective (Basic Heuristic)
    first_person_words = {"i", "me", "my", "we", "our", "you", "your"}
    desc_words = set(re.findall(r'\b\w+\b', description.lower()))
    found_forbidden = first_person_words.intersection(desc_words)
    if found_forbidden:
        errors.append(
            f"STYLE WARNING: Description contains first/second person terms: {found_forbidden}. "
            "Use third-person imperative (e.g., 'Creates...', 'Updates...')."
        )

    # 9. Validate Directory Name Match (requires filepath)
    if filepath:
        parent_dir = os.path.basename(os.path.dirname(os.path.abspath(filepath)))
        if name != parent_dir:
            errors.append(
                f"NAME MISMATCH: name='{name}' but file lives in directory '{parent_dir}'. "
                "The 'name' field must exactly match the parent directory name."
            )

    # 10. Validate Trigger Optimization
    desc_lower = description.lower()
    has_positive_trigger = "use when" in desc_lower
    has_negative_trigger = any(
        phrase in desc_lower
        for phrase in ["don't use", "do not use", "not for", "not use", "avoid"]
    )
    if not has_positive_trigger:
        errors.append(
            "DESCRIPTION WARNING: No positive trigger found. "
            "Include a 'Use when...' phrase to help agents know when to load this skill."
        )
    if not has_negative_trigger:
        errors.append(
            "DESCRIPTION WARNING: No negative trigger found. "
            "Include a 'Don\\'t use for...' phrase to prevent false triggers."
        )

    # 11. Validate Description Describes What Skill Does
    action_verbs = {
        "analyzes", "calculates", "checks", "cleans", "configures",
        "converts", "creates", "deletes", "designs", "extracts",
        "filters", "formats", "generates", "handles", "identifies",
        "implements", "integrates", "manages", "merges", "monitors",
        "organizes", "parses", "processes", "produces", "provides",
        "queries", "reads", "reviews", "searches", "sorts", "splits",
        "summarizes", "supports", "tests", "tracks", "transforms",
        "updates", "validates", "writes"
    }
    desc_words = set(re.findall(r'\b\w+\b', desc_lower))
    if not (action_verbs & desc_words):
        errors.append(
            "DESCRIPTION WARNING: No action verb found describing what the skill does. "
            "Include what the skill accomplishes (e.g., 'Extracts text...', 'Analyzes data...')."
        )

    # 12. Validate SKILL.md Body Line Count (requires filepath)
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        body_lines = 0
        in_frontmatter = False
        frontmatter_closed = False
        for line in lines:
            if line.strip() == "---" and not in_frontmatter:
                in_frontmatter = True
                continue
            if line.strip() == "---" and in_frontmatter and not frontmatter_closed:
                frontmatter_closed = True
                continue
            if frontmatter_closed:
                body_lines += 1
        if body_lines > 500:
            errors.append(
                f"STYLE WARNING: SKILL.md body is {body_lines} lines. "
                "Keep under 500 lines for optimal performance. "
                "Consider splitting content into separate files."
            )

    return errors


def _report_and_exit(errors):
    if errors:
        header = "\n  VALIDATION ISSUES\n  -----------------\n"
        body = "\n".join(f"  * {e}" for e in errors)
        print(f"{header}{body}\n", file=sys.stderr)
        sys.exit(1)
    else:
        print("SUCCESS: Metadata is valid and optimized for discovery.")
        sys.exit(0)


def interactive_mode():
    """Run the script interactively when no CLI arguments are provided."""
    print()
    print("=" * 56)
    print("     SKILL METADATA VALIDATOR - Interactive Mode")
    print("=" * 56)
    print("  [1]  Validate a simple description")
    print("  [2]  Validate a .md file")
    print("  [3]  Validate an entire folder of skills")
    print("  [4]  List folder / sub-folder structure")
    print("  [q]  Quit")
    print("=" * 56)
    print()

    while True:
        choice = input("  Enter your choice: ").strip().lower()
        if choice == "1":
            name = input("Enter skill name: ").strip()
            description = input("Enter skill description: ").strip()
            _report_and_exit(validate_metadata(name, description))
            return
        elif choice == "2":
            path = input("Enter path to .md file: ").strip()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.normpath(os.path.join(script_dir, path))
            if not os.path.isfile(filepath):
                print(f"ERROR: File not found: '{filepath}'", file=sys.stderr)
                sys.exit(1)
            name, description = parse_frontmatter(filepath)
            print(f"Parsed: name='{name}', description={len(description)} chars")
            _report_and_exit(validate_metadata(name, description, filepath=filepath))
            return
        elif choice == "3":
            path = input("Enter path to skill folder: ").strip()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            folder = os.path.normpath(os.path.join(script_dir, path))
            if not os.path.isdir(folder):
                print(f"ERROR: Folder not found: '{folder}'", file=sys.stderr)
                sys.exit(1)
            _validate_folder(folder)
            return
        elif choice == "4":
            path = input("Enter path to folder: ").strip()
            _list_folder_structure(path)
            return
        elif choice == "q":
            print("  Goodbye!")
            sys.exit(0)
        else:
            print("  Invalid choice. Please enter 1, 2, 3, 4, or q.")


def _resolve_path(path):
    """Resolve a path relative to script dir, falling back to CWD if not found."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.normpath(os.path.join(script_dir, path))
    if os.path.exists(candidate):
        return candidate
    # Fallback: resolve relative to CWD
    candidate = os.path.normpath(os.path.join(os.getcwd(), path))
    if os.path.exists(candidate):
        return candidate
    return os.path.abspath(path)


def _list_folder_structure(folder, depth=3):
    """Print an ASCII-safe directory tree of the given folder (up to `depth` levels)."""
    folder = _resolve_path(folder)
    if not os.path.isdir(folder):
        print(f"ERROR: Folder not found: '{folder}'", file=sys.stderr)
        sys.exit(1)

    root_name = os.path.basename(folder)
    print(f"\n  Directory structure of: {folder}\n")
    print(f"  {root_name}/")

    _print_tree(folder, indent="  ", depth=depth)
    print()


def _print_tree(folder, indent, depth):
    """Recursively print directory tree entries."""
    if depth <= 0:
        return
    entries = sorted(os.listdir(folder))
    for i, entry in enumerate(entries):
        entry_path = os.path.join(folder, entry)
        is_last = i == len(entries) - 1
        branch = "+-- " if is_last else "|-- "
        suffix = "/" if os.path.isdir(entry_path) else ""
        print(f"{indent}{branch}{entry}{suffix}")
        if os.path.isdir(entry_path):
            connector = "    " if is_last else "|   "
            _print_tree(entry_path, indent + connector, depth - 1)


def _validate_folder(folder):
    """Validate all .md files in a folder."""
    skill_files = []
    for f in os.listdir(folder):
        fpath = os.path.join(folder, f)
        if os.path.isfile(fpath) and f.endswith(".md"):
            skill_files.append(fpath)
    for entry in sorted(os.listdir(folder)):
        entry_path = os.path.join(folder, entry)
        if os.path.isdir(entry_path):
            for f in os.listdir(entry_path):
                fpath = os.path.join(entry_path, f)
                if os.path.isfile(fpath) and f.endswith(".md"):
                    skill_files.append(fpath)

    if not skill_files:
        print(f"No .md files found in '{folder}' or its subdirectories.", file=sys.stderr)
        sys.exit(1)

    results = []
    for skill_path in skill_files:
        rel = os.path.relpath(skill_path, folder)
        name, description = parse_frontmatter(skill_path)
        errors = validate_metadata(name, description, filepath=skill_path)
        if errors:
            err_text = "\n".join(errors)
            results.append((rel, "FAIL", err_text))
        else:
            results.append((rel, "PASS", ""))

    print(f"\n{'=' * 60}")
    print(f"  Batch Validation Report: {folder}")
    print(f"{'=' * 60}\n")

    passed = sum(1 for r in results if r[1] == "PASS")
    failed = sum(1 for r in results if r[1] != "PASS")

    for rel, status, errs in results:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {icon}  {rel}  {status}")
        if errs:
            for line in errs.splitlines():
                print(f"         * {line}")
        print()

    print(f"{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed, {len(results)} total")
    print(f"{'=' * 60}\n")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate skill metadata for agentskills.io compliance.",
        epilog=(
            "Examples:\n"
            "  python3 validate-metadata.py --name 'my-skill' --description 'Does X.'\n"
            "  python3 validate-metadata.py --skillToValidate path/to/file.md\n"
            "  python3 validate-metadata.py --skillFolder path/to/skills/\n"
            "  python3 validate-metadata.py --listStructure path/to/folder/\n"
            "  python3 validate-metadata.py            (interactive mode)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--name", help="Skill name (lowercase, numbers, single hyphens)")
    parser.add_argument("--description", help="Skill description (max 1024 chars, third-person)")
    parser.add_argument(
        "--skillToValidate",
        help="Path to a .md file. Reads 'name' and 'description' from its YAML frontmatter.",
    )
    parser.add_argument(
        "--skillFolder",
        help="Path to a folder containing skill subdirectories. "
        "Validates every .md file found inside (non-recursive, one level deep).",
    )
    parser.add_argument(
        "--listStructure",
        help="Path to a folder. Prints its directory tree (up to three levels deep) to the console.",
    )

    args = parser.parse_args()

    # No arguments → interactive mode
    if not any(vars(args).values()):
        interactive_mode()
        sys.exit(0)

    if args.skillFolder:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.normpath(os.path.join(script_dir, args.skillFolder))
        if not os.path.isdir(folder):
            print(f"ERROR: Folder not found: '{folder}'", file=sys.stderr)
            sys.exit(1)

        skill_files = []
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            if os.path.isfile(fpath) and f.endswith(".md"):
                skill_files.append(fpath)
        for entry in sorted(os.listdir(folder)):
            entry_path = os.path.join(folder, entry)
            if os.path.isdir(entry_path):
                for f in os.listdir(entry_path):
                    fpath = os.path.join(entry_path, f)
                    if os.path.isfile(fpath) and f.endswith(".md"):
                        skill_files.append(fpath)

        if not skill_files:
            print(f"No .md files found in '{folder}' or its subdirectories.", file=sys.stderr)
            sys.exit(1)

        results = []
        for skill_path in skill_files:
            rel = os.path.relpath(skill_path, folder)
            name, description = parse_frontmatter(skill_path)
            # Pass filepath so directory-name matching works in batch mode
            errors = validate_metadata(name, description, filepath=skill_path)
            if errors:
                err_text = "\n".join(errors)
                results.append((rel, "FAIL", err_text))
            else:
                results.append((rel, "PASS", ""))

        print(f"\n{'=' * 60}")
        print(f"  Batch Validation Report: {folder}")
        print(f"{'=' * 60}\n")

        passed = sum(1 for r in results if r[1] == "PASS")
        failed = sum(1 for r in results if r[1] != "PASS")

        for rel, status, errs in results:
            icon = "[PASS]" if status == "PASS" else "[FAIL]"
            print(f"  {icon}  {rel}  {status}")
            if errs:
                for line in errs.splitlines():
                    print(f"         * {line}")
            print()

        print(f"{'=' * 60}")
        print(f"  Results: {passed} passed, {failed} failed, {len(results)} total")
        print(f"{'=' * 60}\n")

        sys.exit(1 if failed else 0)

    elif args.listStructure:
        _list_folder_structure(args.listStructure)
        sys.exit(0)

    elif args.skillToValidate:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(script_dir, args.skillToValidate))
        if not os.path.isfile(filepath):
            print(f"ERROR: File not found: '{filepath}'", file=sys.stderr)
            sys.exit(1)
        name, description = parse_frontmatter(filepath)
        print(f"Parsed from '{args.skillToValidate}': name='{name}', description={len(description)} chars")
        # Pass filepath so directory-name matching works
        _report_and_exit(validate_metadata(name, description, filepath=filepath))

    elif args.name is not None and args.description is not None:
        # No filepath available, so directory-name check is skipped
        _report_and_exit(validate_metadata(args.name, args.description))

    else:
        parser.error(
            "Provide --skillFolder <path>, --skillToValidate <path>, --listStructure <path>, "
            "OR both --name <name> and --description <text>."
        )