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