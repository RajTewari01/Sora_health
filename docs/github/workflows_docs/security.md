# Security Checks Workflow Configuration

```yaml
# ──────────────────────────────────────────────────────────────
#  SECURITY — Enterprise Vulnerability Scanning
#  Runs on every push and pull request.
#  Covers: Secret Scanning, SAST (Bandit), Dependency Audits
# ──────────────────────────────────────────────────────────────

name: "Security Checks"

on:
  push:
    branches: ["main", "master"]
  pull_request:
    branches: ["main", "master"]

concurrency:
  group: security-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: read

jobs:
  # ── 1. Secret Scanning ─────────────────────────────────────────
  secret-scanning:
    name: "TruffleHog Secret Scanner"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # TruffleHog needs full history to scan commits

      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --debug --only-verified

  # ── 2. SAST (Static Application Security Testing) ──────────────
  sast-bandit:
    name: "Bandit Python SAST"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install Bandit
        run: pip install bandit

      - name: Run Bandit (backend and db scripts)
        # -r: recursive
        # -ll: report only medium and high severity issues
        # -ii: report only medium and high confidence issues
        run: |
          # We use `|| true` so it doesn't fail if the directory doesn't exist yet
          if [ -d "src/backend" ] || [ -d "db" ]; then
            bandit -r src/backend/ db/ -ll -ii
          else
            echo "Target directories not found, skipping SAST."
          fi

  # ── 3. Dependency Vulnerability Audit ─────────────────────────
  dependency-audit:
    name: "Dependency CVE Audit"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install Dependencies & pip-audit
        run: |
          pip install pip-audit
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          fi
          if [ -f pyproject.toml ]; then
            pip install -e .
          fi

      - name: Run pip-audit
        # Scans the active environment for packages with known CVEs
        run: pip-audit

  # ── 4. Next.js (Web) Security ─────────────────────────────────
  nextjs-security:
    name: "Next.js Security (npm audit & njsscan)"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: npm audit (Check Dependencies)
        run: |
          # We use `|| true` so it warns without failing if no package.json is present yet
          if [ -d "src/frontend/web" ] && [ -f "src/frontend/web/package.json" ]; then
            cd src/frontend/web
            npm audit --audit-level=high || true
          else
            echo "Next.js web directory or package.json not found. Skipping."
          fi

      - name: njsscan (Node.js SAST)
        uses: ajinabraham/njsscan-action@master
        with:
          args: 'src/frontend/web/'

  # ── 5. Flutter (Mobile) Security ──────────────────────────────
  flutter-security:
    name: "Flutter Dart Analyzer"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.x"

      - name: Dart Analyze
        run: |
          if [ -d "src/frontend/mobile" ] && [ -f "src/frontend/mobile/pubspec.yaml" ]; then
            cd src/frontend/mobile
            flutter pub get
            flutter analyze
          else
            echo "Flutter mobile directory or pubspec.yaml not found. Skipping."
          fi

  # ── 6. Docker Container Security (Trivy) ──────────────────────
  docker-security:
    name: "Trivy Docker Vulnerability Scanner"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        # This scans the actual Dockerfiles and configurations in your repo
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'

  # ── 7. Infrastructure as Code (IaC) Security ──────────────────
  iac-security:
    name: "Checkov IaC Scanner (Docker Compose)"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Checkov GitHub Action
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: dockerfile,dockercompose
          soft_fail: true # Set to true initially so it warns instead of blocking your workflow immediately

  # ── 8. Open Source License Compliance ──────────────────────────
  license-compliance:
    name: "Trivy License Scanner."
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Trivy License Scanner
        # Scans the repository for problematic open-source licenses (like GPL/AGPL)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          scanners: 'license'
          format: 'table'
          exit-code: '1'
```

### Properties & Actions Breakdown:

- **`on: [push, pull_request]`**: Defines the trigger. This workflow runs automatically whenever someone pushes code to `main` or opens a Pull Request targeting `main`.

- **`concurrency`**: Groups the workflow runs by branch name (`${{ github.ref }}`). If a developer pushes multiple commits quickly, GitHub will manage them efficiently. `cancel-in-progress: false` ensures that actively running security scans are allowed to finish before the new one starts, so you always get a full report.

- **`permissions: contents: read`**: A security best practice. It restricts the GitHub Token so these jobs can only *read* the repository code, not write or change it.

- **`uses: actions/checkout@v4` (Checkout repository)**: 
  - This is the very first step in every single job. It tells the GitHub runner (the cloud server) to download your repository's code so that the security tools actually have files to scan. 
  - In the TruffleHog job, we use `fetch-depth: 0` alongside checkout. By default, checkout only downloads the very latest commit (depth: 1). TruffleHog needs the entire history (`depth: 0`) to search for secrets hidden deep in old commits.

- **Environment Setup Actions (`actions/setup-*`)**:
  - **`setup-python@v5`**: Installs a specific version of Python (3.10) onto the runner so we can run `pip install` and use tools like Bandit and pip-audit.
  - **`setup-node@v4`**: Installs Node.js version 20 to run `npm audit` for the frontend.
  - **`subosito/flutter-action@v2`**: Installs the Flutter SDK so we can run Dart analysis on the mobile app.

- **Security Scanners Used**:
  - **`trufflesecurity/trufflehog@main`**: Scans the commit history for leaked API keys, passwords, and tokens. We use `extra_args: --only-verified` to dramatically reduce false positives; it actually tests the found secrets against live APIs to see if they are real.
  - **`ajinabraham/njsscan-action@master`**: A dedicated Static Application Security Testing (SAST) tool explicitly built for Node.js/JavaScript, finding insecure code patterns in the Next.js app.
  - **`aquasecurity/trivy-action@master` (Vulnerability Mode)**: Deeply analyzes Dockerfiles and container layers to find vulnerabilities in the base OS libraries (like Debian/Alpine). It is strictly set to fail (`exit-code: '1'`) if it finds `CRITICAL` or `HIGH` vulnerabilities.
  - **`aquasecurity/trivy-action@master` (License Mode)**: We run a second Trivy job explicitly with `scanners: 'license'`. This scans your entire repository to find problematic, viral Open Source licenses (like GPL or AGPL) that could legally jeopardize proprietary enterprise code.
  - **`bridgecrewio/checkov-action@master`**: Analyzes Infrastructure as Code (Docker Compose). We set `soft_fail: true` so it initially just gives you warnings without blocking your Pull Request completely if your infrastructure isn't perfect yet.

**How to Use**:
    - Add the `security.yml` file to `.github/workflows/`.
    - No manual execution is required. Opening a PR automatically spawns 7 parallel servers to run all these checks simultaneously.
    - Review the GitHub Actions UI on your PR to see detailed breakdown logs of any security failures.

**Extra things which you should know**:

1. **Conditional Shell Logic (`if [ -d ... ]`)**
   - You'll notice bash `if` statements throughout the YAML (e.g., checking if `src/backend` exists before running Bandit). This ensures that if certain parts of the project haven't been created yet, the workflow gracefully skips the step instead of crashing in a fiery failure.
2. **Graceful Failures (`|| true`)**
   - In the Next.js `npm audit` step, we append `|| true`. This means even if `npm audit` finds vulnerabilities and exits with an error code, GitHub Actions is tricked into seeing it as a success, so it warns you without permanently blocking the deployment.

#### File structure:

```text
Sora_Health_System/
├── .github/
│   └── workflows/
│       └── security.yml       <- The workflow file configuration.
├── docs/
│   └── github/
│       └── workflows_docs/
│           └── security.md    <- This documentation file!
└── README.md
```
