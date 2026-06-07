# Git Configuration Reference

This document explains every section of the project's `.gitconfig` file — what each setting does, why it exists, and the real-world problem it solves.

---

## Full Configuration

```ini
[user]
    name = RajTewari01
    email = tewari765@gmail.com
    signingkey = ~/.ssh/id_ed25519.pub

[commit]
    gpgsign = true

[gpg]
    format = ssh

[core]
    editor = nvim
    pager = delta

[interactive]
    diffFilter = delta --color-only

[alias]
    status = status -sb
    log = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
    tree = log --graph --decorate --oneline --all
    stage_all = add -A
    commit_file = commit -F

[pull]
    rebase = true

[help]
    autocorrect = 1

[init]
    defaultBranch = main

[delta]
    navigate = true

[merge]
    conflictstyle = zdiff3

[rerere]
    enabled = true

[push]
    autoSetupRemote = true

[diff]
    colorMoved = default

[rebase]
    autoStash = true

[fetch]
    prune = true
```

---

## Section-by-Section Breakdown

### `[user]` — Identity

| Key     | Value              | Purpose                                              |
|---------|--------------------|------------------------------------------------------|
| `name`  | `RajTewari01`      | The author name stamped on every commit.             |
| `email` | `tewari765@gmail.com` | The email linked to your GitHub account for commits. |
| `signingkey` | `~/.ssh/id_ed25519.pub` | The path to your public SSH key used to sign commits. |

> [!TIP]
> **Work Profile Setup:** To automatically switch to a company email inside a specific folder, add this to your **global** `~/.gitconfig`:
> ```ini
> [includeIf "gitdir:D:/Work/"]
>     path = D:/.gitconfig-work
> ```
> Then create `D:/.gitconfig-work` containing only:
> ```ini
> [user]
>     email = raj@sorahealth.com
> ```

---

### `[commit]` & `[gpg]` — Commit Signing (Verified Badge)

| Section | Key       | Value  | Purpose                                                                 |
|---------|-----------|--------|-------------------------------------------------------------------------|
| `[commit]` | `gpgsign` | `true` | Forces Git to digitally sign every single commit you make.              |
| `[gpg]`    | `format`  | `ssh`  | Tells Git to use modern, simple SSH keys for signing instead of GPG keys. |

**The Problem It Solves:**
By default, anyone can put any email in their `.gitconfig` and pretend to be you. By signing your commits with your unique SSH key, GitHub verifies your identity and places a green **"Verified"** badge next to all your commits, proving they actually came from you.

> [!TIP]
> **Work Profile Setup:** To automatically switch to a company email inside a specific folder, add this to your **global** `~/.gitconfig`:
> ```ini
> [includeIf "gitdir:D:/Work/"]
>     path = D:/.gitconfig-work
> ```
> Then create `D:/.gitconfig-work` containing only:
> ```ini
> [user]
>     email = raj@sorahealth.com
> ```

---

### `[core]` — Editor & Pager

| Key      | Value   | Purpose                                                                 |
|----------|---------|-------------------------------------------------------------------------|
| `editor` | `nvim`  | Opens Neovim for commit messages and interactive rebases.               |
| `pager`  | `delta` | Routes all `git diff`, `git log`, and `git show` output through Delta. |

**Why Neovim over VSCode?**
When Git needs you to type a commit message, `nvim` opens instantly in the same terminal window. `code --wait` would launch a separate graphical VSCode window, adding seconds of delay and breaking your terminal flow.

**What is Delta?**
Delta is a syntax-highlighting pager that replaces Git's ugly default diff output with beautiful, color-coded, side-by-side comparisons directly in your terminal.

> [!IMPORTANT]
> Delta must be installed separately before this setting works:
> ```powershell
> winget install dandavison.delta
> ```

---

### `[interactive]` — Staging Filter

| Key          | Value                  | Purpose                                                    |
|--------------|------------------------|------------------------------------------------------------|
| `diffFilter` | `delta --color-only`   | Applies Delta syntax highlighting during `git add -p` (interactive staging). |

When you use `git add -p` to selectively stage chunks of code, this ensures the displayed hunks are syntax-highlighted through Delta instead of raw, uncolored text.

---

### `[alias]` — Command Shortcuts

| Alias         | Expands To                          | What It Does                                                     |
|---------------|-------------------------------------|------------------------------------------------------------------|
| `status`      | `status -sb`                        | Shows a **s**hort, **b**ranch-aware status instead of the verbose default. |
| `log`         | `log --graph --pretty=format:...`   | Displays a colorized, single-line commit graph with hash, message, time, and author. |
| `tree`        | `log --graph --decorate --oneline --all` | Visualizes the entire branch topology as an ASCII tree.     |
| `stage_all`   | `add -A`                            | Stages all changes (new, modified, and deleted files) in one command. |
| `commit_file` | `commit -F`                         | Reads the commit message from a file instead of typing it inline. |

**Usage Examples:**
```bash
git status       # → Short, clean output like: "## main...origin/main"
git tree         # → Full ASCII branch graph of every branch
git stage_all    # → Stage everything at once
git commit_file COMMIT_MSG.txt  # → Commit using a pre-written message file
```

---

### `[pull]` — Pull Strategy

| Key      | Value  | Purpose                                                              |
|----------|--------|----------------------------------------------------------------------|
| `rebase` | `true` | Replays your local commits on top of the remote branch instead of creating a merge commit. |

**The Problem It Solves:**
Without this, every `git pull` creates an ugly `Merge branch 'main' of ...` commit that clutters your history. With `rebase = true`, your commit history stays perfectly linear and clean.

---

### `[help]` — Typo Auto-Correction

| Key           | Value | Purpose                                                         |
|---------------|-------|-----------------------------------------------------------------|
| `autocorrect` | `1`   | If you mistype a command (e.g., `git statsu`), Git waits 0.1 seconds and then automatically runs the closest match (`git status`). |

---

### `[init]` — Default Branch Name

| Key             | Value  | Purpose                                                    |
|-----------------|--------|------------------------------------------------------------|
| `defaultBranch` | `main` | Every `git init` creates a `main` branch instead of the legacy `master`. |

---

### `[delta]` — Delta Pager Settings

| Key        | Value  | Purpose                                                           |
|------------|--------|-------------------------------------------------------------------|
| `navigate` | `true` | Enables keyboard navigation in diffs: press `n` to jump to the next file, `N` to jump back. |

> [!WARNING]
> **Dependency:** `[delta] navigate = true` does absolutely nothing on its own. It **requires** `[core] pager = delta` to be set first. Without the pager directive, Git never routes output through Delta, so navigate has nothing to act on. Always ensure both sections exist together.

**Why This Matters:**
When reviewing a diff that touches 10+ files, instead of endlessly scrolling, you press `n` to instantly skip to the next changed file — like GitHub's "Files Changed" tab, but in your terminal.

---

### `[merge]` — Conflict Resolution Style

| Key             | Value   | Purpose                                                           |
|-----------------|---------|-------------------------------------------------------------------|
| `conflictstyle` | `zdiff3`| Shows a **three-way diff** during merge conflicts: your code, their code, AND the original "common ancestor" code. |

**The Problem It Solves:**
The default conflict style only shows "yours" vs "theirs", making it impossible to understand what the code looked like *before* either side changed it. `zdiff3` adds a third `|||||||` section showing the original, making conflict resolution dramatically easier.

---

### `[rerere]` — Conflict Memory (**RE**use **RE**corded **RE**solution)

| Key       | Value  | Purpose                                                          |
|-----------|--------|------------------------------------------------------------------|
| `enabled` | `true` | Git memorizes how you resolve merge conflicts. If the exact same conflict appears again (e.g., during a rebase), Git automatically applies the same resolution. |

---

### `[push]` — Push Behavior

| Key               | Value  | Purpose                                                       |
|--------------------|--------|---------------------------------------------------------------|
| `autoSetupRemote` | `true` | Eliminates the `--set-upstream` error. When you push a new branch for the first time, Git automatically links it to the remote. |

**The Problem It Solves:**
Without this, pushing a new branch forces you to type: `git push --set-upstream origin feature-branch`. With this enabled, just `git push` works instantly.

---

### `[diff]` — Diff Enhancements

| Key          | Value     | Purpose                                                        |
|--------------|-----------|----------------------------------------------------------------|
| `colorMoved` | `default` | Detects lines that were **moved** (not changed) and highlights them in a distinct color (purple/cyan) instead of showing red deletions + green additions. |

**The Problem It Solves:**
If you move a function from the top of a file to the bottom, the default diff shows 50 red lines and 50 green lines — making it look like you rewrote everything. `colorMoved` recognizes the move and displays it differently, so code reviewers instantly understand nothing was actually changed.

---

### `[rebase]` — Rebase Safety Net

| Key         | Value  | Purpose                                                         |
|-------------|--------|-----------------------------------------------------------------|
| `autoStash` | `true` | Automatically stashes uncommitted changes before a rebase, then re-applies them after the rebase completes. |

**The Problem It Solves:**
If you have unsaved work and try to `git pull --rebase`, Git normally refuses with: *"Cannot rebase: You have unstaged changes."* This setting silently handles it for you.

---

### `[fetch]` — Fetch Cleanup

| Key     | Value  | Purpose                                                           |
|---------|--------|-------------------------------------------------------------------|
| `prune` | `true` | Automatically removes local references to remote branches that have been deleted on GitHub. |

**The Problem It Solves:**
Without this, `git branch -a` slowly accumulates dozens of stale `remotes/origin/old-feature` entries for branches that no longer exist, cluttering your branch list.

---

## How to Apply

> [!IMPORTANT]
> This `.gitconfig` file lives at the **repository level** (`d:\Sora_Health_System\.gitconfig`). To apply these settings globally across all projects on your machine, copy the file to your home directory:
> ```powershell
> Copy-Item .\.gitconfig $HOME\.gitconfig
> ```
> Or apply individual settings with:
> ```powershell
> git config --global pull.rebase true
> git config --global push.autoSetupRemote true
> ```

## Required External Tools

| Tool    | Install Command                        | Purpose                           |
|---------|----------------------------------------|-----------------------------------|
| Neovim  | `winget install Neovim.Neovim`         | Terminal-based code editor        |
| Delta   | `winget install dandavison.delta`      | Syntax-highlighted diff pager     |
| Lazygit | `winget install JesseDuffield.lazygit` | Interactive terminal Git UI       |
| fzf     | `winget install junegunn.fzf`          | Fuzzy file and history finder     |
| bat     | `winget install sharkdp.bat`           | Syntax-highlighted `cat` replacement |