import os
import ast
from pathlib import Path

# ===== CONFIGURATION =====
PROJECT_ROOT = Path(
    "/home/patex1987/development/mean_max_python_engine/src/python_prototypes/"
)  # adjust to your project folder
ENTRY_FILE = PROJECT_ROOT / "input_handler.py"
OUTPUT_FILE = Path("merged_codingame_solution.py")
PROJECT_PACKAGE = "python_prototypes"  # your package name prefix
# =========================


def find_dependencies(file_path: Path, visited=None):
    """Recursively find all internal project dependencies."""
    if visited is None:
        visited = set()
    file_path = file_path.resolve()

    if file_path in visited or not file_path.exists():
        return []

    visited.add(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    dependencies = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith(PROJECT_PACKAGE):
                rel_path = node.module.replace(".", "/") + ".py"
                abs_path = PROJECT_ROOT / rel_path.split(f"{PROJECT_PACKAGE}/")[-1]
                if abs_path.exists():
                    dependencies.append(abs_path)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(PROJECT_PACKAGE):
                    rel_path = alias.name.replace(".", "/") + ".py"
                    abs_path = PROJECT_ROOT / rel_path.split(f"{PROJECT_PACKAGE}/")[-1]
                    if abs_path.exists():
                        dependencies.append(abs_path)

    merged = []
    for dep in dependencies:
        merged.extend(find_dependencies(dep, visited))

    merged.append(file_path)
    return merged


def merge_files(entry_file: Path, output_file: Path):
    """Flatten all internal modules into a single .py file."""
    all_files = find_dependencies(entry_file)
    all_files = list(dict.fromkeys(all_files))  # preserve order, remove dups

    print(f"🧩 Found {len(all_files)} modules to merge.")
    print(f"📦 Writing to {output_file}...\n")

    written_imports = set()

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# ======= MERGED CODINGAME SOLUTION =======\n\n")

        for path in all_files:
            rel_path = path.relative_to(PROJECT_ROOT)
            out.write(f"\n# ===== FILE: {rel_path} =====\n")

            with open(path, "r", encoding="utf-8") as f:
                in_multiline_import = False

                for line in f:
                    stripped = line.strip()

                    # --- skip project internal imports (including multiline ones) ---
                    if stripped.startswith(f"from {PROJECT_PACKAGE}") or stripped.startswith(
                        f"import {PROJECT_PACKAGE}"
                    ):
                        if "(" in stripped and not ")" in stripped:
                            in_multiline_import = True  # start of multiline import
                        continue

                    # --- inside a continued multiline import ---
                    if in_multiline_import:
                        if ")" in stripped:
                            in_multiline_import = False  # end of block
                        continue

                    # --- keep only unique stdlib imports ---
                    if stripped.startswith(("import ", "from ")):
                        if line not in written_imports:
                            written_imports.add(line)
                            out.write(line)
                        continue

                    # --- write all other lines normally ---
                    out.write(line)

    print(f"✅ Done! Output: {output_file.absolute()}")


if __name__ == "__main__":
    merge_files(ENTRY_FILE, OUTPUT_FILE)
    # uv tool run --from python-minifier pyminify merged_codingame_solution.py --output minified_codingame.py --remove-literal-statements
    # uv tool run --from python-minifier pyminify merged_codingame_solution.py --output minified_codingame_larger.py --remove-literal-statements --no-rename-locals --remove-asserts --remove-debug
    # black -S -l 120 ./minified_codingame_larger.py
