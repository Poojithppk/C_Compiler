# PROJECT SETUP COMMANDS

## Virtual Environment Setup

### Create Virtual Environment
```bash
# Navigate to project directory
cd "d:\my projects\C_Compiler"

# Create virtual environment
python -m venv compiler_env
```

### Activate Virtual Environment
```bash
# Windows Command Prompt
compiler_env\Scripts\activate

# Windows PowerShell
compiler_env\Scripts\Activate.ps1

# For deactivation (when needed)
deactivate
```

## Dependency Installation

### Install Core Dependencies
```bash
# Ensure virtual environment is activated first
pip install --upgrade pip

# GUI Framework
pip install tkinter-dev>=8.6
pip install PyQt5>=5.15.0

# Visualization Libraries
pip install matplotlib>=3.5.0
pip install networkx>=2.6.0
pip install graphviz>=0.20.0

# Development Tools
pip install pytest>=7.0.0
pip install pytest-cov>=3.0.0
pip install black>=22.0.0
pip install flake8>=4.0.0

# Documentation
pip install sphinx>=4.5.0
pip install sphinx-rtd-theme>=1.0.0

# Utility Libraries
pip install colorama>=0.4.0
pip install rich>=12.0.0
pip install click>=8.0.0
```

### Create Requirements File
```bash
# Generate requirements.txt
pip freeze > requirements.txt
```

### Install from Requirements (for future setup)
```bash
# Install from requirements.txt
pip install -r requirements.txt
```

## Git Setup

### Initialize Repository
```bash
# Initialize Git repository
git init

# Add remote origin (replace with your repository URL)
git remote add origin <your-repository-url>

# Create .gitignore
echo "compiler_env/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo "*.pyd" >> .gitignore
echo ".coverage" >> .gitignore
echo "htmlcov/" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
echo "*.egg-info/" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo ".vscode/" >> .gitignore
echo "temp/" >> .gitignore
echo "*.log" >> .gitignore
```

### Initial Commit
```bash
# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Project structure and documentation"

# Push to remote repository
git push -u origin main
```

## Development Environment

### Install Development Extensions (VS Code)
```bash
# Install Python extension
code --install-extension ms-python.python

# Install Git extensions
code --install-extension eamodio.gitlens

# Install formatting extensions
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8

# Install testing extensions
code --install-extension ms-python.pytest
```

### Configure VS Code Settings
```json
// Create .vscode/settings.json
{
    "python.defaultInterpreterPath": "./compiler_env/Scripts/python.exe",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

## Project Validation

### Test Environment Setup
```bash
# Test Python installation
python --version

# Test pip installation
pip --version

# Test virtual environment
where python
```

### Run Initial Tests
```bash
# Create and run basic test
python -c "print('Environment setup successful!')"

# Test GUI framework
python -c "import tkinter; print('Tkinter available')"
python -c "import PyQt5; print('PyQt5 available')"

# Test visualization libraries
python -c "import matplotlib; print('Matplotlib available')"
python -c "import networkx; print('NetworkX available')"
```

## Quick Start Commands

### Daily Development Workflow
```bash
# 1. Activate environment
compiler_env\Scripts\activate

# 2. Pull latest changes
git pull origin main

# 3. Start development
# Run main application
python src/main.py

# Run tests
pytest tests/

# Format code
black src/

# Check code quality
flake8 src/
```

### Complete Setup Script (PowerShell)
```powershell
# complete_setup.ps1
# Complete project setup script

Write-Host "Setting up Advanced Compiler Project..." -ForegroundColor Green

# Navigate to project directory
Set-Location "d:\my projects\C_Compiler"

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv compiler_env

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "compiler_env\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install PyQt5 matplotlib networkx graphviz pytest pytest-cov black flake8 sphinx sphinx-rtd-theme colorama rich click

# Generate requirements.txt
Write-Host "Generating requirements.txt..." -ForegroundColor Yellow
pip freeze > requirements.txt

# Initialize git
Write-Host "Initializing Git repository..." -ForegroundColor Yellow
git init

# Create .gitignore
@"
compiler_env/
__pycache__/
*.pyc
*.pyo
*.pyd
.coverage
htmlcov/
dist/
build/
*.egg-info/
.pytest_cache/
.vscode/
temp/
*.log
"@ | Out-File -FilePath .gitignore -Encoding UTF8

Write-Host "Setup complete! Virtual environment created and activated." -ForegroundColor Green
Write-Host "Run 'python src/main.py' to start the application." -ForegroundColor Cyan
```

### Run Setup Script
```powershell
# Save the script as setup.ps1 and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

## Troubleshooting

### Common Issues and Solutions

#### Virtual Environment Issues
```bash
# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative activation methods
compiler_env\Scripts\python.exe -m pip install --upgrade pip
```

#### Package Installation Issues
```bash
# Update pip first
python -m pip install --upgrade pip

# Install packages individually if batch install fails
pip install PyQt5
pip install matplotlib
# ... continue with each package
```

#### Git Issues
```bash
# Configure Git user (if first time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Fix line ending issues
git config --global core.autocrlf true
```

## Project Verification

### Verify Complete Setup
```bash
# Check all installations
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import tkinter, PyQt5, matplotlib, networkx, pytest; print('All packages available')"
git --version
```

### Expected Output
```
Python: 3.8+ (or higher)
All packages available
git version 2.x.x (or higher)
```

Project setup is complete when all verification commands run without errors.