# Hygiene Checks (Scripts)

```python
import sys
import json
import tomllib
from pathlib import Path

# Directories and file extensions to ignore
IGNORE_DIRS = {".git", "evenv", "node_modules", "__pycache__"}
IGNORE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".bmp", ".zip", ".svg"}

def is_ignored(path: Path):
    return any(part in IGNORE_DIRS for part in path.parts)

def check_file(filepath: Path):
    if filepath.suffix.lower() in IGNORE_EXTS:
        return True

    success = True
    # Normalize path to POSIX style for consistent GitHub Actions output
    filepath_str = filepath.as_posix() 
    
    # 1. JSON Lint
    if filepath.suffix.lower() == ".json":
        try:
            with filepath.open("r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            print(f"::error file={filepath_str}::Invalid JSON syntax: {e}", file=sys.stderr)
            success = False
            
    # 2. TOML Lint
    if filepath.suffix.lower() == ".toml":
        try:
            with filepath.open("rb") as f:
                tomllib.load(f)
        except Exception as e:
            print(f"::error file={filepath_str}::Invalid TOML syntax: {e}", file=sys.stderr)
            success = False

    # Binary checks (BOM and Trailing Newlines)
    try:
        content_bytes = filepath.read_bytes()
    except IOError:
        return success
        
    # Skip empty files
    if not content_bytes:
        return success 

    # 3. Check for UTF-8 BOM
    if content_bytes.startswith(b'\xef\xbb\xbf'):
        print(f"::error file={filepath_str}::UTF-8 BOM detected", file=sys.stderr)
        success = False
        
    # 4. Check missing trailing newline
    if content_bytes[-1] != 0x0a:
        print(f"::warning file={filepath_str}::Missing trailing newline", file=sys.stderr)
        success = False

    # Text checks (Whitespace and Merge Conflicts)
    try:
        skip_whitespace = filepath.suffix.lower() in {".md", ".lock"}
        
        with filepath.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                clean_line = line.rstrip('\r\n')
                
                # 5. Trailing whitespace
                if not skip_whitespace and (clean_line.endswith(" ") or clean_line.endswith("\t")):
                    print(f"::warning file={filepath_str},line={line_num}::Trailing whitespace found", file=sys.stderr)
                    
                # 6. Merge conflict markers
                if line.startswith("<<<<<<< ") or line.startswith("=======\n") or line.startswith(">>>>>>> "):
                    print(f"::error file={filepath_str},line={line_num}::Merge conflict markers found", file=sys.stderr)
                    success = False
    except Exception:
        pass # Ignore decoding errors for non-text files

    return success

def main():
    all_success = True
    
    # We can still use rglob to iterate over all files
    for filepath in Path(".").rglob("*"):
        if filepath.is_dir() or is_ignored(filepath):
            continue
            
        if not check_file(filepath):
            all_success = False

    if not all_success:
        sys.exit(1)
        
    print("All hygiene checks passed!")

if __name__ == "__main__":
    main()
```



> [!NOTE]
> - import sys
> - import json
> - import tomllib
> - from pathlib import Path
> - These are the important standard library modules we need to import for running the script. They require no external pip installations.

### How it Works:

- **Directory/Extension Ignores**: 
  - `IGNORE_DIRS` and `IGNORE_EXTS` define directories (like `.git`, `node_modules`) and binary extensions (like `.png`, `.zip`) to skip. This dramatically speeds up the script and prevents false positives.

- **File Traversal**: 
  - Uses `Path(".").rglob("*")` to recursively scan every file in the repository, seamlessly filtering out ignored directories using the `path.parts` property.

- **Syntax Linting**: 
  - Parses and validates JSON files using `json.load()` and TOML files using `tomllib.load()`.

- **Binary & Formatting Checks**: 
  - **UTF-8 BOM**: Ensures files do not start with a Byte Order Mark (`\xef\xbb\xbf`), which breaks some parsers.
  - **Trailing Newlines**: Verifies that every file ends with a standard POSIX newline (`0x0a`).

- **Text-Level Checks**: 
  - **Trailing Whitespace**: Scans every line for unnecessary spaces/tabs at the end (skipping `.md` and `.lock` files).
  - **Merge Conflicts**: Aggressively scans for Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) to ensure no unresolved conflicts are merged.

**How to Use**:
    - Place the `hygiene_checks.py` script inside your repository.
    - Run the script locally with `python .github/scripts/hygiene_checks.py`.
    - Integrated in GitHub Actions, the script's `print(f"::error file={filepath}::...")` logs will magically turn into inline annotations directly on your Pull Requests!

**Extra things which you should know**:

1. `pathlib` vs `os`
- The script uses modern Python `pathlib.Path` instead of the legacy `os` module. It allows checking file extensions with `.suffix` instead of `os.path.splitext()`, making the code incredibly clean.

2. `sys.exit(1)` (CI/CD Safety)
- If any check fails, a flag is set, and the script eventually calls `sys.exit(1)`. This non-zero exit code ensures that your GitHub Actions CI pipeline fails and blocks the PR from merging.

#### File structure:

```text
Sora_Health_System/
├── .github/
│   ├── scripts/
│   │   └── hygiene_checks.py      <- The actual python script execution file.
│   └── workflows/
│       └── lints.yml              <- The GitHub Action that runs the script.
├── docs/
│   └── github/
│       └── scripts_docs/
│           └── hygiene_checks.md  <- This documentation file!
└── README.md
```
