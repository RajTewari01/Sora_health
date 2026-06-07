# Documentation Quality Checks Workflow

```yaml
# ──────────────────────────────────────────────────────────────
#  DOCS — Documentation Quality & Completeness
#  Validates docstrings, Markdown links, README, and code TODOs.
# ──────────────────────────────────────────────────────────────

name : "Docs checker -- documentation quality and completeness"

on:
    push:
        branches : ["main","master"]
        paths:
          - "docs/**"
          - "src/**"
          - "README.md"
          - "*.md"
    pull_request :
        branches : ["main","master"]

concurrency:
  group: docs-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents : read

jobs:

  # ── Docstring Coverage ──────────────────────────────────────
  docstring-check:
    name : "Python docstring-checks"
    runs-on : ubuntu-latest

    steps :
      - name : "check the repository."
        uses : actions/checkout@v4

      - name : "setup python 3.10"
        uses : actions/setup-python@v5
        with:
          python-version: "3.10"

      - name : "install pydocstyle"
        run : pip install pydocstyle

      - name : "pydocstyle lint <<check>>."
        run : |
          pydocstyle src/ \
            --convention=google \
            --add-ignore=D100,D104,D105,D107 \
            --count || true
        # D100: module docstring, D104: package docstring
        # D105: magic method, D107: __init__ docstring
        # Using || true to warn without failing until codebase matures

  # ── Markdown Link Validation ────────────────────────────────
  link-check:
    name : "Markdown links"
    runs-on : ubuntu-latest

    steps :
      - name : "check the repository."
        uses : actions/checkout@v4

      - name : "check markdown links."
        uses : gaurav-nelson/github-action-markdown-link-check@v1
        with:
          config-file: ".github/mlc_config.json"
          folder-path: "docs/,."
          file-extension: ".md"
          check-modified-files-only: "yes"
          use-quiet-mode: "yes"
        continue-on-error: true

  # ── README Validation ───────────────────────────────────────
  readme-check:
    name : "README quality"
    runs-on : ubuntu-latest

    steps :
      - name : "check the repository."
        uses : actions/checkout@v4

      - name : "verify README exists and is non-empty."
        run : |
          if [ ! -f "README.md" ]; then
            echo "::error::README.md is missing"
            exit 1
          fi

          LINES=$(wc -l < README.md)
          if [ "$LINES" -lt 5 ]; then
            echo "::warning::README.md has only $LINES lines — consider adding project documentation"
          fi

      - name : "check for required README sections."
        run : |
          for section in "##" ; do
            if ! grep -q "$section" README.md; then
              echo "::warning::README.md has no headings — consider structuring with ## sections"
              break
            fi
          done

  # ── TODO / FIXME Scanner ────────────────────────────────────
  todo-scanner:
    name : "TODO/FIXME tracker"
    runs-on : ubuntu-latest

    steps :
      - name : "check the repository."
        uses : actions/checkout@v4

      - name : "scan for TODO/FIXME/HACK comments."
        run : |
          echo "### Open code annotations ###"
          echo ""

          echo "-- TODO --"
          git grep -rIn 'TODO' -- 'src/' 'tests/' '*.py' ':!evenv/' || echo "  (none)"
          echo ""

          echo "-- FIXME --"
          git grep -rIn 'FIXME' -- 'src/' 'tests/' '*.py' ':!evenv/' || echo "  (none)"
          echo ""

          echo "-- HACK --"
          git grep -rIn 'HACK' -- 'src/' 'tests/' '*.py' ':!evenv/' || echo "  (none)"

          # This job always passes — it is informational
          exit 0
```

### Properties & Actions Breakdown:

- **`on: push & pull_request`**: Defines the trigger. However, notice the specific `paths:` configuration! This workflow is smart—it only runs if changes were made inside `docs/**`, `src/**`, `README.md`, or any `*.md` files. This saves GitHub cloud credits by not running if you only touched something unrelated like a Dockerfile or package.json.

- **`uses: actions/checkout@v4` (Checkout repository)**: 
  - Standard step to fetch your code onto the cloud runner so the scripts have something to analyze.

- **Documentation Jobs**:

  - **1. Python docstring-checks (`pydocstyle`)**:
    - Installs and runs `pydocstyle` to ensure your backend Python code is documented properly using the `google` convention standard.
    - We specifically ignore rules `D100`, `D104`, `D105`, and `D107` to keep it pragmatic (e.g. not forcing a docstring on every single `__init__.py` file).
    - It uses `|| true` at the end so it just warns you instead of violently breaking your Pull Request if you forget a docstring.

  - **2. Markdown links (`github-action-markdown-link-check`)**:
    - Scans every `.md` file to ensure no links are dead or returning 404s. It cleverly ties directly into the `.github/mlc_config.json` file we configured previously to ignore things like localhost and GitHub UI links!
    - **Note on the `with:` block**: The settings like `folder-path`, `config-file`, and `use-quiet-mode` are custom inputs specifically programmed for *this exact GitHub Action*. You cannot use these inputs on other tools (like Bandit or TruffleHog).
    - **Note on `continue-on-error: true`**: Unlike the `with:` block, `continue-on-error` is a universal GitHub Actions feature. You **can** use this on absolutely any job or step! It tells GitHub: "Even if this step fails, pretend it passed and keep running."

  - **3. README quality (Custom Bash)**:
    - A custom, super-fast bash script that enforces basic README quality standards.
    - It verifies that `README.md` actually exists and has more than 5 lines of text.
    - **The `for section in "##"` bash loop**: This uses a quick `grep -q` (quiet grep) to check if the file contains a level-2 markdown heading (`##`). If it `! grep -q` (does NOT find it), it breaks the loop and triggers a GitHub warning `::warning::`.

  - **4. TODO/FIXME tracker (Custom Bash)**:
    - Runs a lightning-fast `git grep` command across the entire codebase searching for `TODO`, `FIXME`, and `HACK` comments.
    - **Why use `echo ""`?**: You'll notice `echo ""` sprinkled throughout this bash script. This simply prints a blank, empty line to the console. It is used entirely for formatting, ensuring the output logs in the GitHub UI have nice spacing and aren't an unreadable wall of text!
    - It ends with `exit 0`, meaning it will **always pass**. This is purely an informational job so reviewers can look at the Actions UI and instantly see how much technical debt is being introduced in the Pull Request.

**How to Use**:
    - This workflow runs automatically when you push documentation or code changes to `main`.
    - You can look at the output of the **TODO/FIXME tracker** job inside the GitHub Actions UI during a code review to get a quick summary of open tasks.

#### File structure:

```text
Sora_Health_System/
├── .github/
│   └── workflows/
│       └── docs.yml           <- The workflow file configuration.
├── docs/
│   └── github/
│       └── workflows_docs/
│           └── docs.md        <- This documentation file!
└── README.md
```
