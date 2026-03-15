# 🚀 KATS Project - Contribution Guidelines

**Urban Rooftop Farming AI System**

Thank you for contributing to KATS! This document outlines how to work with our Git/GitHub workflow, ensuring smooth collaboration and clean code.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Git Workflow (Git Flow)](#git-workflow)
3. [Branch Naming Convention](#branch-naming-convention)
4. [Commit Message Format](#commit-message-format)
5. [Pull Request Process](#pull-request-process)
6. [Code Quality Standards](#code-quality-standards)
7. [Common Issues & Solutions](#common-issues--solutions)
8. [Resources](#resources)

---

## Getting Started

### Prerequisites
- Git installed (`git --version`)
- GitHub account with repository access
- Python 3.8+ installed
- Virtual environment setup

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/KATS.git
cd KATS

# 2. Switch to develop branch (main integration branch)
git checkout develop

# 3. Pull latest changes
git pull origin develop

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements-dev.txt

# 6. Verify installation
python -c "import streamlit; print(streamlit.__version__)"
```

---

## Git Workflow

We follow **Git Flow** branching strategy:

```
main (production-ready)
  ├─ develop (integration branch - main development)
  │   ├─ feature/username-task
  │   ├─ bugfix/username-bug
  │   ├─ ui/username-component
  │   └─ docs/username-update
```

### Step-by-Step Workflow

#### 1. Start a New Feature

```bash
# Always start from develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-username-task-name

# Example:
# git checkout -b feature/marita-water-prediction-model
# git checkout -b bugfix/ali-fusion-weight-bug
# git checkout -b ui/sara-neumorphic-buttons
```

#### 2. Work on Your Feature

```bash
# Make edits to files
# Your IDE will show changes

# Check status
git status

# Stage your changes
git add src/models/ann_model.py
# or all changes:
git add .

# Commit with meaningful message (see Commit Format below)
git commit -m "feat: implement water prediction ANN model"

# Make multiple commits as needed
git commit -m "feat: add hyperparameter optimization"
git commit -m "test: add unit tests for ANN model"
```

#### 3. Push to GitHub

```bash
# Push your branch to GitHub
git push origin feature/your-username-task-name

# Or simply:
git push
```

#### 4. Create Pull Request (PR)

**Via GitHub Web Interface:**

1. Go to https://github.com/YOUR_ORG/KATS
2. Click on "Pull requests" tab
3. Click "New Pull Request"
4. **Base:** `develop` ← **Compare:** `feature/your-username-task-name`
5. Fill in PR details (see [PR Template](#pull-request-template))
6. Click "Create Pull Request"

#### 5. Code Review & Merge

```bash
# Wait for:
# ✓ Code review approval (min. 1 reviewer)
# ✓ CI/CD checks to pass
# ✓ No merge conflicts

# Merge via GitHub UI:
# Click "Squash and merge" (recommended for clean history)
```

#### 6. Cleanup

```bash
# After PR is merged:

# Switch back to develop
git checkout develop

# Pull latest changes
git pull origin develop

# Delete local branch
git branch -d feature/your-username-task-name

# Delete remote branch (GitHub handles this automatically, but you can do it manually)
git push origin --delete feature/your-username-task-name

# Start next feature
git checkout -b feature/username-next-task
```

---

## Branch Naming Convention

Use **kebab-case** with prefixes:

```
feature/[username]-[task-description]
bugfix/[username]-[bug-description]
ui/[username]-[component-name]
docs/[username]-[doc-update]
refactor/[username]-[module-name]
test/[username]-[test-suite]
chore/[username]-[maintenance-task]
```

### Examples

✅ **Good:**
- `feature/marita-ann-water-prediction`
- `bugfix/ali-fusion-weight-calculation`
- `ui/sara-dark-mode-implementation`
- `docs/mehmet-api-documentation`
- `refactor/emre-data-pipeline-optimization`

❌ **Bad:**
- `marita-ann` (too vague)
- `fix-bug` (no username)
- `my-feature` (unclear what it is)
- `Feature/Water` (mixed case)

---

## Commit Message Format

We follow **Conventional Commits** standard:

```
[type]: [description]
[blank line]
[optional body]
[blank line]
[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add RLHF feedback processor` |
| `fix` | Bug fix | `fix: resolve fusion weight calculation` |
| `ui` | UI/UX changes | `ui: implement neumorphic button design` |
| `docs` | Documentation | `docs: add RLHF mechanism guide` |
| `refactor` | Code refactor | `refactor: modularize data pipeline` |
| `perf` | Performance | `perf: optimize model inference speed` |
| `test` | Tests | `test: add SVM disease detection tests` |
| `chore` | Maintenance | `chore: update dependencies` |
| `bugfix` | Important bug | `bugfix: fix critical model loading error` |

### Examples

```bash
# Simple feature
git commit -m "feat: implement water tank level visualization"

# With description (use for complex changes)
git commit -m "feat: add RLHF feedback processor

- Implement Human-in-the-Loop feedback mechanism
- Add approval/modify/reject buttons
- Track learning progress with feedback history
- Update fusion weights based on user feedback

Closes #42"

# Bug fix
git commit -m "fix: resolve NaN values in ANN water prediction"

# UI update
git commit -m "ui: enhance metric widget with gradient text effects"

# Documentation
git commit -m "docs: add comprehensive RLHF training guide"

# Tests
git commit -m "test: add unit tests for random forest health model"

# Refactoring
git commit -m "refactor: split monolithic app.py into modular components"
```

---

## Pull Request Process

### PR Template

When opening a PR, use this template:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] New feature (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change
- [ ] Documentation update
- [ ] UI/UX improvement

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] No regressions detected

## Related Issues
Closes #123

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation/docstrings updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

### PR Best Practices

✅ **DO:**
- Keep PRs focused (single feature/fix)
- Keep PRs small (< 400 lines changes)
- Write descriptive titles & descriptions
- Reference related issues (`Closes #123`)
- Test locally before pushing
- Respond to review comments promptly
- Keep branch updated with develop

❌ **DON'T:**
- Create huge PR with 10 features
- Leave PRs open without updates
- Use vague titles like "Update stuff"
- Ignore failing CI/CD checks
- Merge without approval
- Force push after opening PR

---

## Code Quality Standards

### Pre-commit Checks

Run before committing:

```bash
# Format code
black src/

# Sort imports
isort src/

# Lint
flake8 src/

# Type checking
mypy src/

# All at once
black src/ && isort src/ && flake8 src/ && mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/unit/test_models.py

# Specific test
pytest tests/unit/test_models.py::test_ann_output
```

### Code Style Guidelines

- **Python:** PEP 8 (enforced by `black`)
- **Line length:** 100 characters
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Docstrings:** Google-style docstrings
- **Type hints:** Use type hints in all functions

### Example Function

```python
def calculate_water_requirement(soil_moisture: float, temperature: float) -> float:
    """
    Calculate optimal water requirement based on environmental conditions.
    
    Args:
        soil_moisture: Current soil moisture percentage (0-100)
        temperature: Air temperature in Celsius
        
    Returns:
        Recommended water reduction percentage (0-100)
        
    Raises:
        ValueError: If inputs are out of valid range
        
    Example:
        >>> calculate_water_requirement(58.0, 22.1)
        45.3
    """
    if not (0 <= soil_moisture <= 100):
        raise ValueError("soil_moisture must be between 0-100")
    
    water_req = (100 - soil_moisture) * (temperature / 30)
    return min(max(water_req, 0), 100)
```

---

## Common Issues & Solutions

### Issue 1: "Your branch is behind origin/develop"

```bash
git pull origin develop
```

### Issue 2: Merge Conflicts

```bash
# When pulling
git pull origin develop
# VS Code will show conflicts, resolve them, then:
git add .
git commit -m "fix: resolve merge conflicts"
git push
```

### Issue 3: "I committed to develop by accident"

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1
git checkout -b feature/username-oops-task
git commit -m "feat: the actual feature"
```

### Issue 4: Wrong Commit Message

```bash
# Amend last commit
git commit --amend -m "feat: correct message"
git push --force-with-lease  # Use only on your branch!
```

### Issue 5: Need to Stash Work

```bash
# Save work temporarily
git stash

# List stashes
git stash list

# Pop latest stash
git stash pop

# Or apply specific stash
git stash apply stash@{0}
```

### Issue 6: Accidentally Deleted Files

```bash
# Recover deleted file
git restore src/models/ann_model.py

# Or from last commit
git checkout HEAD -- src/models/ann_model.py
```

---

## Git Commands Quick Reference

```bash
# Check status
git status

# View changes
git diff                          # Unstaged changes
git diff --staged                 # Staged changes
git diff develop                  # vs develop branch

# View history
git log --oneline                 # Simple log
git log --graph --all --decorate  # Branching visualization

# Undoing changes
git restore file.py               # Discard changes (unstaged)
git restore --staged file.py      # Unstage file
git revert <commit>               # Create new commit undoing changes
git reset --soft HEAD~1           # Undo last commit, keep changes
git reset --hard HEAD~1           # Undo last commit, discard changes

# Branching
git branch                        # List local branches
git branch -a                     # List all branches
git branch -d branch-name         # Delete branch
git branch -D branch-name         # Force delete branch

# Stashing
git stash                         # Save work temporarily
git stash list                    # List stashes
git stash pop                     # Apply and remove latest stash
git stash apply stash@{0}         # Apply specific stash

# Remote operations
git remote -v                     # View remotes
git fetch origin                  # Download changes
git pull origin develop           # Fetch and merge
git push origin branch-name       # Push branch to remote
```

---

## Resources

- [Git Official Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
- [Pro Git Book](https://git-scm.com/book/en/v2)

---

## Questions?

- 💬 Ask in project chatroom or Discord
- 📧 Email: team@kats-farm.com
- 👥 Check existing issues/discussions on GitHub
- 🆘 Create a GitHub Discussion for complex questions

---

**Happy coding! 🌱🚀**
