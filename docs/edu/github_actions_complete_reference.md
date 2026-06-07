# GitHub Actions — Complete YAML Reference Guide

> [!NOTE]
> This is an educational reference that explains **every single property** you can use in a GitHub Actions workflow YAML file, where it goes, and what it does.

---

## 1. Workflow-Level Properties (Top of the file)

These properties sit at the very top of your `.yml` file. They define the identity, triggers, and global settings for the entire workflow.

```yaml
# ── name ──────────────────────────────────────────────────────
name: "My Workflow Name"
# What it does: Gives your workflow a human-readable name.
# Where it shows: In the GitHub Actions UI tab on your repository.
# Required? No, but strongly recommended.
```

```yaml
# ── run-name ──────────────────────────────────────────────────
run-name: "Deploy by @${{ github.actor }}"
# What it does: Customizes the name of each individual run.
# Where it shows: In the list of workflow runs (not the workflow itself).
# Example output: "Deploy by @RajTewari01"
```

---

### 1.1 `on:` — Trigger Events

This is **the most important property**. It defines WHEN your workflow runs.

```yaml
# ── Basic Triggers ────────────────────────────────────────────
on: push                     # Runs on every push to any branch
on: [push, pull_request]     # Runs on both push AND pull requests
```

```yaml
# ── Branch Filtering ──────────────────────────────────────────
on:
  push:
    branches: ["main", "master"]        # Only run on pushes to main/master
    branches-ignore: ["feature/**"]     # Run on all EXCEPT feature branches
```

```yaml
# ── Path Filtering (Smart Triggers) ──────────────────────────
on:
  push:
    paths:
      - "src/**"              # Only run if files inside src/ changed
      - "docs/**"             # OR files inside docs/ changed
      - "*.md"                # OR any markdown file in root changed
    paths-ignore:
      - "**/*.md"             # Ignore ALL markdown file changes
```

```yaml
# ── Tag Triggers ──────────────────────────────────────────────
on:
  push:
    tags:
      - "v*"                  # Run when a tag like v1.0.0 is pushed
```

```yaml
# ── Scheduled (Cron) Triggers ────────────────────────────────
on:
  schedule:
    - cron: "0 6 * * 1"      # Every Monday at 6:00 AM UTC
    - cron: "*/15 * * * *"   # Every 15 minutes
# Cron format: minute hour day-of-month month day-of-week
# Use https://crontab.guru/ to build cron expressions
```

```yaml
# ── Manual Trigger (workflow_dispatch) ────────────────────────
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Deploy to which environment?"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production
# This adds a "Run workflow" button in the GitHub UI
# with a dropdown to pick the environment!
```

```yaml
# ── Other Useful Triggers ────────────────────────────────────
on:
  issues:
    types: [opened, labeled]       # When an issue is opened or labeled
  release:
    types: [published]             # When a release is published
  workflow_call:                   # Makes this workflow reusable by other workflows
  repository_dispatch:             # Triggered by external API calls
```

---

### 1.2 `concurrency:` — Prevent Duplicate Runs

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```

| Property | What it does |
|---|---|
| `group:` | A string that groups workflow runs together. Runs with the same group name are queued. Using `${{ github.ref }}` groups by branch, so each branch gets its own queue. |
| `cancel-in-progress: true` | If a new run starts while an old one is still going, **kill the old one**. Set to `false` if you want the old run to finish first (important for deployments!). |

---

### 1.3 `permissions:` — Security Token Restrictions

```yaml
permissions:
  contents: read          # Can read repo files (most common)
  contents: write         # Can push commits, create releases
  issues: write           # Can create/edit issues
  pull-requests: write    # Can comment on PRs
  packages: write         # Can publish to GitHub Packages
  actions: read           # Can read workflow run data
  security-events: write  # Can upload SARIF security reports
```

> [!IMPORTANT]
> **Enterprise best practice**: Always use the **least privilege** principle. If your workflow only needs to read code, set `contents: read`. Never give `write` access unless the job specifically needs it. This limits the blast radius if a malicious action is used.

---

### 1.4 `env:` — Global Environment Variables

```yaml
env:
  PYTHON_VERSION: "3.10"
  NODE_VERSION: "20"
  REGISTRY: ghcr.io
```

These variables are available to **every single job and step** in the entire workflow. Individual jobs/steps can override them with their own `env:` block.

---

### 1.5 `defaults:` — Global Defaults

```yaml
defaults:
  run:
    shell: bash
    working-directory: src/backend
```

Sets the default shell and working directory for **all** `run:` steps in the workflow. Individual steps can still override these.

---

## 2. Job-Level Properties

Jobs live inside the `jobs:` key. Each job runs on a separate cloud server (runner). By default, **all jobs run in parallel**.

```yaml
jobs:
  my-job-id:                              # Unique identifier (no spaces, use hyphens)
    name: "Human Readable Job Name"       # Display name in the GitHub UI
    runs-on: ubuntu-latest                # Which cloud server to use
```

### 2.1 `runs-on:` — Choose Your Cloud Server

| Value | What it is |
|---|---|
| `ubuntu-latest` | Ubuntu Linux (most common, cheapest) |
| `ubuntu-22.04` | Specific Ubuntu version |
| `windows-latest` | Windows Server |
| `macos-latest` | macOS (most expensive — 10x cost!) |
| `self-hosted` | Your own physical server |
| `[self-hosted, linux, x64]` | Self-hosted with specific labels |

---

### 2.2 `needs:` — Job Dependencies (Run Order)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: build                # Wait for 'build' to finish first
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: [build, test]        # Wait for BOTH 'build' AND 'test'
    runs-on: ubuntu-latest
    steps: [...]
```

Without `needs:`, all 3 jobs would run at the same time. With `needs:`, you create a pipeline: `build → test → deploy`.

---

### 2.3 `if:` — Conditional Execution (Job Level)

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    # This job ONLY runs on the main branch. Completely skipped on feature branches.

  notify-on-failure:
    if: failure()
    # This job ONLY runs if a previous job failed.

  always-cleanup:
    if: always()
    # This job runs no matter what — even if previous jobs failed or were cancelled.

  skip-bot-commits:
    if: github.actor != 'dependabot[bot]'
    # Skip this job if Dependabot made the commit.
```

#### Common `if:` Expressions

| Expression | When it's true |
|---|---|
| `github.event_name == 'push'` | Only on push events |
| `github.event_name == 'pull_request'` | Only on pull requests |
| `github.ref == 'refs/heads/main'` | Only on the main branch |
| `contains(github.event.head_commit.message, '[skip ci]')` | If the commit message contains `[skip ci]` |
| `success()` | If all previous jobs passed |
| `failure()` | If any previous job failed |
| `always()` | Always, regardless of previous results |
| `cancelled()` | If the workflow was manually cancelled |

---

### 2.4 `strategy:` — Matrix Builds (Test Multiple Versions)

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest]
      fail-fast: false        # Don't cancel other matrix jobs if one fails
      max-parallel: 2         # Run at most 2 matrix jobs simultaneously

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

This creates **8 parallel jobs** (4 Python versions × 2 operating systems). Enterprise teams use this to guarantee their code works everywhere.

| Property | What it does |
|---|---|
| `matrix:` | Defines the combinations to test |
| `fail-fast: true` (default) | If one combo fails, cancel all others immediately |
| `fail-fast: false` | Let all combos finish so you see ALL failures |
| `max-parallel:` | Limit how many run at the same time (saves billing) |

---

### 2.5 `environment:` — Deployment Protection

```yaml
jobs:
  deploy-production:
    environment:
      name: production
      url: https://sorahealth.com
```

This links the job to a **GitHub Environment**. Environments can have:
- **Required reviewers** — A senior engineer must manually approve before deployment
- **Wait timers** — Force a 30-minute delay before deploying
- **Branch restrictions** — Only allow deployments from `main`
- **Environment secrets** — Secrets that are ONLY available to this specific environment

---

### 2.6 `services:` — Spin Up Docker Containers

```yaml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
```

This spins up real PostgreSQL and Redis containers alongside your job! Your test code can connect to `localhost:5432` and `localhost:6379` as if they were real databases.

---

### 2.7 Other Job-Level Properties

```yaml
jobs:
  my-job:
    timeout-minutes: 30       # Kill the entire job after 30 minutes
    continue-on-error: true   # Job fails but workflow still passes
    container:                # Run the entire job inside a Docker container
      image: node:20
      env:
        NODE_ENV: production
    outputs:                  # Pass data to downstream jobs
      version: ${{ steps.get-version.outputs.version }}
```

---

## 3. Step-Level Properties

Steps live inside a job's `steps:` array. Each step is one action or command.

### 3.1 The Two Types of Steps

```yaml
steps:
  # TYPE 1: Use a pre-built GitHub Action
  - name: "Checkout repository"
    uses: actions/checkout@v4       # Uses someone else's pre-built action

  # TYPE 2: Run a shell command directly
  - name: "Install dependencies"
    run: pip install -r requirements.txt    # Runs a raw terminal command
```

> [!IMPORTANT]
> A step can have `uses:` OR `run:`, **never both**. They are mutually exclusive.

---

### 3.2 `uses:` — Pre-Built Actions

```yaml
- uses: actions/checkout@v4                    # Official GitHub action
- uses: actions/setup-python@v5                # Official Python setup
- uses: docker://alpine:3.18                   # Run a Docker image directly
- uses: ./.github/actions/my-custom-action     # Local action in your repo
```

The `with:` block passes **inputs** to the action. Each action defines its own unique inputs:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0          # This input is specific to checkout
    ref: develop            # Checkout a specific branch

- uses: actions/setup-python@v5
  with:
    python-version: "3.10"  # This input is specific to setup-python
    cache: "pip"            # Cache pip dependencies for speed
```

> [!WARNING]
> The `with:` inputs are **NOT universal**. `fetch-depth` only works with `checkout`. `python-version` only works with `setup-python`. Always check the action's README to see what inputs it accepts.

---

### 3.3 `run:` — Shell Commands

```yaml
# Single-line command
- run: echo "Hello World"

# Multi-line command (use the pipe | character)
- run: |
    echo "Line 1"
    echo "Line 2"
    pip install -r requirements.txt
    pytest tests/

# Change the shell
- run: Write-Host "Hello from PowerShell"
  shell: pwsh

# Change the working directory
- run: npm install
  working-directory: src/frontend/web
```

---

### 3.4 Universal Step Properties

These work on **ANY** step, whether it uses `uses:` or `run:`:

```yaml
- name: "My Step"                    # Human-readable label (optional but recommended)
  id: my-step-id                     # Unique ID to reference outputs later
  if: success()                      # Conditional execution
  continue-on-error: true            # Step fails but job keeps running
  timeout-minutes: 10                # Kill the step after 10 minutes
  env:                               # Environment variables for this step only
    MY_SECRET: ${{ secrets.API_KEY }}
    DEBUG: "true"
```

| Property | Where it works | What it does |
|---|---|---|
| `name:` | Any step | Display name in the UI |
| `id:` | Any step | Unique identifier to reference outputs |
| `if:` | Any step | Conditionally skip the step |
| `continue-on-error:` | Any step | Don't fail the job if this step fails |
| `timeout-minutes:` | Any step | Hard time limit |
| `env:` | Any step | Set environment variables |
| `shell:` | Only `run:` steps | Force a specific shell |
| `working-directory:` | Only `run:` steps | Change directory before running |
| `with:` | Only `uses:` steps | Pass inputs to the action |

---

## 4. Variables & Expressions

### 4.1 `${{ }}` — Expression Syntax

Everything inside `${{ }}` is evaluated by GitHub before the step runs.

```yaml
- run: echo "Branch is ${{ github.ref }}"
- run: echo "Actor is ${{ github.actor }}"
- run: echo "Event is ${{ github.event_name }}"
```

### 4.2 Context Objects

| Context | What it contains | Example |
|---|---|---|
| `github.*` | Info about the event, repo, branch | `github.ref`, `github.actor`, `github.sha` |
| `env.*` | Environment variables | `env.MY_VAR` |
| `secrets.*` | Repository secrets | `secrets.API_KEY` |
| `vars.*` | Repository variables (non-secret) | `vars.DEPLOY_URL` |
| `steps.*` | Outputs from previous steps | `steps.my-step.outputs.result` |
| `needs.*` | Outputs from previous jobs | `needs.build.outputs.version` |
| `matrix.*` | Current matrix value | `matrix.python-version` |
| `runner.*` | Info about the runner machine | `runner.os`, `runner.temp` |
| `inputs.*` | Manual workflow_dispatch inputs | `inputs.environment` |

### 4.3 Common Patterns with Secrets

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

steps:
  - run: echo "Deploying..."
    env:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

> [!CAUTION]
> **NEVER** `echo` a secret! GitHub automatically masks secrets in logs, but if you manipulate the string (e.g., base64 encode it), it can leak. Always treat secrets as invisible.

---

## 5. Passing Data Between Steps & Jobs

### 5.1 Between Steps (Same Job)

```yaml
steps:
  - name: Set version
    id: get-version
    run: echo "version=1.2.3" >> $GITHUB_OUTPUT

  - name: Use version
    run: echo "The version is ${{ steps.get-version.outputs.version }}"
```

### 5.2 Between Jobs (Different Runners)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: echo "version=1.2.3" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying version ${{ needs.build.outputs.version }}"
```

---

## 6. Artifacts & Caching

### 6.1 Upload/Download Artifacts (Share Files Between Jobs)

```yaml
# Job 1: Build and upload
- uses: actions/upload-artifact@v4
  with:
    name: my-build
    path: dist/

# Job 2: Download and use
- uses: actions/download-artifact@v4
  with:
    name: my-build
    path: dist/
```

### 6.2 Caching Dependencies (Speed Up Workflows)

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-
```

This caches your pip packages. If `requirements.txt` hasn't changed, it skips the download entirely—saving minutes on every run!

---

## 7. GitHub Actions Log Commands

These special `echo` prefixes are intercepted by the GitHub Actions system and turned into UI annotations:

```bash
# Error — red ❌ annotation on the PR
echo "::error file=app.py,line=10::Syntax error found"

# Warning — yellow ⚠️ annotation on the PR
echo "::warning file=app.py,line=25::Deprecated function used"

# Notice — blue ℹ️ annotation
echo "::notice::Build completed successfully"

# Debug — only visible if debug logging is enabled
echo "::debug::Variable value is $MY_VAR"

# Group — collapsible section in the logs
echo "::group::Install Dependencies"
pip install -r requirements.txt
echo "::endgroup::"

# Mask — hide a value from all future logs
echo "::add-mask::my-secret-value"

# Set environment variable for ALL subsequent steps
echo "MY_VAR=hello" >> $GITHUB_ENV

# Set output for other steps/jobs to consume
echo "result=success" >> $GITHUB_OUTPUT

# Add a directory to PATH for ALL subsequent steps
echo "/my/custom/bin" >> $GITHUB_PATH
```

---

## 8. Complete Workflow Template

Here is a production-ready template combining everything above:

```yaml
name: "CI/CD Pipeline"
run-name: "CI by @${{ github.actor }} on ${{ github.ref_name }}"

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:
    inputs:
      deploy:
        description: "Deploy after tests?"
        type: boolean
        default: false

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  pull-requests: write

env:
  PYTHON_VERSION: "3.10"

defaults:
  run:
    shell: bash

jobs:
  # ── Lint ────────────────────────────────────────────────────
  lint:
    name: "Code Quality"
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"

      - run: pip install ruff
      - run: ruff check src/

  # ── Test ────────────────────────────────────────────────────
  test:
    name: "Tests (${{ matrix.python-version }})"
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - run: |
          pip install -r requirements.txt
          pytest tests/ --junitxml=results.xml

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: results.xml

  # ── Deploy ──────────────────────────────────────────────────
  deploy:
    name: "Deploy to Production"
    needs: test
    if: github.ref == 'refs/heads/main' && (github.event_name == 'push' || inputs.deploy)
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://sorahealth.com

    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        run: echo "Deploying to production..."
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

  # ── Notify ──────────────────────────────────────────────────
  notify-failure:
    name: "Notify on Failure"
    needs: [lint, test, deploy]
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - run: echo "::error::Pipeline failed! Check the logs above."
```

---

## 9. Quick Reference Cheat Sheet

### Where Can Each Property Go?

| Property | Workflow | Job | Step |
|---|---|---|---|
| `name:` | ✅ | ✅ | ✅ |
| `on:` | ✅ | ❌ | ❌ |
| `permissions:` | ✅ | ✅ | ❌ |
| `env:` | ✅ | ✅ | ✅ |
| `defaults:` | ✅ | ✅ | ❌ |
| `concurrency:` | ✅ | ✅ | ❌ |
| `if:` | ❌ | ✅ | ✅ |
| `runs-on:` | ❌ | ✅ | ❌ |
| `needs:` | ❌ | ✅ | ❌ |
| `strategy:` | ❌ | ✅ | ❌ |
| `services:` | ❌ | ✅ | ❌ |
| `environment:` | ❌ | ✅ | ❌ |
| `timeout-minutes:` | ❌ | ✅ | ✅ |
| `continue-on-error:` | ❌ | ✅ | ✅ |
| `outputs:` | ❌ | ✅ | ❌ |
| `container:` | ❌ | ✅ | ❌ |
| `uses:` | ❌ | ❌ | ✅ |
| `run:` | ❌ | ❌ | ✅ |
| `with:` | ❌ | ❌ | ✅ (only `uses:`) |
| `id:` | ❌ | ❌ | ✅ |
| `shell:` | ❌ | ❌ | ✅ (only `run:`) |
| `working-directory:` | ❌ | ❌ | ✅ (only `run:`) |
