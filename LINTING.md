# Code Quality and Linting Setup

This document describes the comprehensive code quality and linting setup for the Football Stats Application.

## 🛠️ Tools Installed

### Core Linting Tools
- **MyPy (1.8.0)** - Static type checking for Python
- **Flake8 (7.0.0)** - Style and syntax checking (PEP 8 compliance)
- **Bandit (1.7.5)** - Security vulnerability analysis
- **Black (24.1.1)** - Automatic code formatting
- **isort (5.13.2)** - Import statement sorting and organization
- **pre-commit (3.6.0)** - Git hook framework for automated checks

## 📁 Configuration Files

### `.flake8`
Configures Flake8 style checking with:
- Line length: 88 characters (compatible with Black)
- Excludes: venv, __pycache__, pgdata, migrations
- Ignores conflicts with Black formatting
- Maximum complexity: 10
- Per-file ignore patterns for specific cases

### `mypy.ini`
Configures MyPy type checking with:
- Python version: 3.10
- Relaxed settings for Flask/SQLAlchemy compatibility
- Import error handling for third-party packages
- Excludes development and generated files

### `.bandit`
Configures Bandit security analysis with:
- Excludes: development directories and files
- Confidence levels: HIGH, MEDIUM
- Severity levels: MEDIUM, HIGH
- Allows asserts in non-production code

### `pyproject.toml`
Contains configuration for:
- **Black**: 88-character line length, Python 3.10 target
- **isort**: Black-compatible profile, known first/third-party imports

### `.pre-commit-config.yaml`
Defines Git hooks for automated quality checks:
- Black formatting
- isort import sorting
- Flake8 style checking
- MyPy type checking
- Bandit security analysis
- General pre-commit hooks (trailing whitespace, file endings, etc.)

## 🚀 Usage

### Manual Commands

#### Individual Tools
```bash
# Format code
black app/ import_players.py
isort app/ import_players.py

# Check style and syntax
flake8 app/ import_players.py

# Type checking
mypy app/ import_players.py

# Security analysis
bandit -r app/ import_players.py
```

#### Using Make Commands
```bash
# Run all linting tools
make lint

# Format code (black + isort)
make format

# Check if formatting is correct
make format-check

# Individual tool checks
make style-check    # Flake8
make type-check     # MyPy
make security      # Bandit

# Install development dependencies
make install-dev

# View all available commands
make help
```

#### Using the Comprehensive Script
```bash
# Run all linting tools with colored output
./lint.sh
```

### Automated Git Hooks

Setup pre-commit hooks to run automatically on git commits:
```bash
# Install pre-commit hooks
make setup-pre-commit

# Or manually:
pre-commit install

# Run on all files
pre-commit run --all-files
```

## ✅ Current Status

### Passing Tools
- ✅ **Black**: Code formatting is consistent
- ✅ **isort**: Import order is correct  
- ✅ **Flake8**: No style or syntax issues
- ✅ **Bandit**: No security issues (with appropriate #nosec comments)

### Warnings/Notes
- ⚠️ **MyPy**: Some type checking issues with SQLAlchemy models (expected with current configuration)

## 🔧 Integration

### Docker Integration
The linting tools are included in `requirements.txt` but excluded from the Docker production build to keep images lean.

### CI/CD Ready
This setup is ready for integration with:
- GitHub Actions
- GitLab CI
- Jenkins
- Any CI/CD system that supports Python

### IDE Integration
Configuration files work with popular IDEs:
- VS Code (with Python extensions)
- PyCharm
- Sublime Text
- Vim/Neovim

## 📋 Quality Standards

### Code Style
- PEP 8 compliance via Flake8
- Consistent formatting via Black
- Organized imports via isort
- Maximum line length: 88 characters
- Maximum complexity: 10

### Security
- No hardcoded secrets
- No SQL injection vulnerabilities
- No unsafe file operations
- Documented exceptions for development needs

### Type Safety
- Gradual typing approach
- Third-party library compatibility
- SQLAlchemy model compatibility
- Flexible configuration for Flask apps

## 🎯 Benefits

1. **Consistency**: All code follows the same style guidelines
2. **Security**: Automated security vulnerability detection
3. **Quality**: Catches potential bugs and style issues early
4. **Automation**: Git hooks prevent committing poorly formatted code
5. **Team Collaboration**: Reduces code review friction
6. **Maintainability**: Clean, well-organized codebase

## 🔄 Maintenance

### Updating Tools
```bash
# Update all linting dependencies
pip install --upgrade mypy flake8 bandit black isort pre-commit

# Update pre-commit hooks
pre-commit autoupdate
```

### Adding New Rules
1. Update the relevant configuration file (.flake8, mypy.ini, etc.)
2. Test changes with `make lint`
3. Update pre-commit hooks if necessary
4. Document changes in this file

This setup ensures high code quality standards while remaining developer-friendly and CI/CD ready.
