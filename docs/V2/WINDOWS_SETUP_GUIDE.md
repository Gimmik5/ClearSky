# 🪟 ClearSky V2.0 - Windows Setup Guide

This guide shows you how to set up ClearSky V2.0 on Windows. You have **3 options** - pick the one that works best for you!

---

## 🎯 Option 1: PowerShell Script (Recommended) ⭐

**Best for:** Most Windows users - simple and native to Windows

### How to Run:

1. **Open PowerShell in your project directory:**
   - Open File Explorer
   - Navigate to your ClearSky project folder
   - Hold `Shift` + Right-click in the folder
   - Select "Open PowerShell window here" (or "Open in Windows Terminal")

2. **Run the setup script:**
   ```powershell
   # If you get an execution policy error, run this first:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Then run the setup script:
   .\setup_v2_structure.ps1
   ```

3. **That's it!** The script will create all folders and files.

### Troubleshooting:

**Error: "Cannot be loaded because running scripts is disabled"**
```powershell
# Run this once:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
.\setup_v2_structure.ps1
```

**Error: "File not found"**
- Make sure you're in the correct directory
- Check that `setup_v2_structure.ps1` is in your current folder
- Use `Get-Location` to see where you are
- Use `Get-ChildItem` to see files in current directory

---

## 🎯 Option 2: Git Bash (If you have Git installed)

**Best for:** Users who have Git for Windows installed

### How to Run:

1. **Open Git Bash in your project directory:**
   - Open File Explorer
   - Navigate to your ClearSky project folder
   - Right-click in the folder
   - Select "Git Bash Here"

2. **Run the bash script:**
   ```bash
   # Make it executable
   chmod +x setup_v2_structure.sh
   
   # Run it
   ./setup_v2_structure.sh
   ```

3. **Done!** All folders and files are created.

### How to get Git Bash:
- Download Git for Windows: https://git-scm.com/download/win
- During installation, make sure "Git Bash Here" is selected
- After install, right-click in any folder → "Git Bash Here"

---

## 🎯 Option 3: Manual Setup (No scripts needed)

**Best for:** If you prefer to do it manually or scripts aren't working

### Step-by-Step:

1. **Open Command Prompt or PowerShell in your project folder**

2. **Copy and paste these commands one by one:**

```powershell
# Create main directories
New-Item -ItemType Directory -Force -Path config
New-Item -ItemType Directory -Force -Path data\migrations
New-Item -ItemType Directory -Force -Path data\storage
New-Item -ItemType Directory -Force -Path analysis\ml\models
New-Item -ItemType Directory -Force -Path analysis\ml\training
New-Item -ItemType Directory -Force -Path hardware
New-Item -ItemType Directory -Force -Path web\routes
New-Item -ItemType Directory -Force -Path web\templates\gallery
New-Item -ItemType Directory -Force -Path web\templates\viewer
New-Item -ItemType Directory -Force -Path web\static\css
New-Item -ItemType Directory -Force -Path web\static\js
New-Item -ItemType Directory -Force -Path web\static\img
New-Item -ItemType Directory -Force -Path web\components
New-Item -ItemType Directory -Force -Path utils
New-Item -ItemType Directory -Force -Path tests\test_analysis
New-Item -ItemType Directory -Force -Path tests\test_data
New-Item -ItemType Directory -Force -Path tests\test_hardware
New-Item -ItemType Directory -Force -Path tests\test_web
New-Item -ItemType Directory -Force -Path scripts
New-Item -ItemType Directory -Force -Path docs

# Create __init__.py files (Python packages)
New-Item -ItemType File -Force -Path config\__init__.py
New-Item -ItemType File -Force -Path data\__init__.py
New-Item -ItemType File -Force -Path data\migrations\__init__.py
New-Item -ItemType File -Force -Path data\storage\__init__.py
New-Item -ItemType File -Force -Path analysis\__init__.py
New-Item -ItemType File -Force -Path analysis\ml\__init__.py
New-Item -ItemType File -Force -Path hardware\__init__.py
New-Item -ItemType File -Force -Path web\__init__.py
New-Item -ItemType File -Force -Path web\routes\__init__.py
New-Item -ItemType File -Force -Path web\components\__init__.py
New-Item -ItemType File -Force -Path utils\__init__.py
New-Item -ItemType File -Force -Path tests\__init__.py

# Create module placeholder files
New-Item -ItemType File -Force -Path config\settings.py
New-Item -ItemType File -Force -Path config\database_config.py
New-Item -ItemType File -Force -Path config\hardware_config.py
New-Item -ItemType File -Force -Path data\models.py
New-Item -ItemType File -Force -Path data\schema.py
New-Item -ItemType File -Force -Path data\operations.py
New-Item -ItemType File -Force -Path data\manager.py
New-Item -ItemType File -Force -Path analysis\core.py
New-Item -ItemType File -Force -Path analysis\brightness.py
New-Item -ItemType File -Force -Path analysis\color.py
New-Item -ItemType File -Force -Path hardware\poller.py
New-Item -ItemType File -Force -Path web\app.py
New-Item -ItemType File -Force -Path web\routes\main_routes.py
New-Item -ItemType File -Force -Path web\routes\api_routes.py
New-Item -ItemType File -Force -Path utils\logger.py
New-Item -ItemType File -Force -Path utils\shutdown.py
```

---

## 📁 Verify Your Setup

After running any of the options above, verify the structure was created:

### Using Command Prompt:
```cmd
tree /F /A
```

### Using PowerShell:
```powershell
Get-ChildItem -Recurse -Directory | Select-Object FullName
```

### Using File Explorer:
- Navigate to your project folder
- You should see these new folders:
  - config/
  - data/
  - analysis/
  - hardware/
  - web/
  - utils/
  - tests/
  - scripts/
  - docs/

---

## 🔧 Next Steps After Setup

### 1. Create .env file

**Option A: Copy command (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Option B: Manual:**
- Copy `.env.example` file
- Rename the copy to `.env`
- Open in your favorite text editor
- Update with your settings (ESP32 IP, etc.)

### 2. Install Python Dependencies

**Open Command Prompt or PowerShell:**
```powershell
# Make sure you're in your project directory
pip install -r requirements.txt
```

**If you get "pip not found":**
```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### 3. Create Git Branch

**Using Git Bash or Command Prompt:**
```bash
git checkout -b v2.0-restructure
git add .
git commit -m "feat: V2.0 folder structure"
```

---

## 💡 Windows Tips

### Working Directory

**To see where you are:**
```powershell
# PowerShell
Get-Location

# Command Prompt
cd
```

**To navigate to your project:**
```powershell
# PowerShell
Set-Location C:\path\to\your\clearsky\project

# Command Prompt
cd C:\path\to\your\clearsky\project
```

### File Paths

Windows uses backslashes (`\`) in paths, but Python works with both:
- `C:\Users\You\clearsky` (Windows)
- `C:/Users/You/clearsky` (Also works in Python)

In your `.env` file, you can use either:
```
DATABASE_PATH=./clearsky.db
IMAGE_DIR=./images/
```

### Common Commands

| Task | PowerShell | Command Prompt |
|------|-----------|----------------|
| List files | `Get-ChildItem` or `ls` | `dir` |
| Change directory | `Set-Location` or `cd` | `cd` |
| Create file | `New-Item -ItemType File -Path file.txt` | `type nul > file.txt` |
| Copy file | `Copy-Item` | `copy` |
| Show file content | `Get-Content` or `cat` | `type` |

---

## 🐛 Troubleshooting

### "Python not found"

**Check if Python is installed:**
```powershell
python --version
```

**If not installed:**
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### "pip not found"

**Use python -m pip instead:**
```powershell
python -m pip install -r requirements.txt
```

### "Permission denied"

**Run PowerShell as Administrator:**
- Press `Windows key`
- Type "PowerShell"
- Right-click "Windows PowerShell"
- Select "Run as administrator"

### Path too long error

Windows has a 260 character path limit. If you get this error:
- Move your project closer to C:\ (e.g., `C:\projects\clearsky\`)
- Or enable long paths (Windows 10+):
  - Run as admin: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`

---

## 🔍 Quick Reference

### Opening Terminal in Project Folder

**Method 1: File Explorer**
1. Navigate to your project folder
2. Hold `Shift` + Right-click in empty space
3. Select "Open PowerShell window here"

**Method 2: Windows Terminal (Windows 11)**
1. Navigate to your project folder
2. Right-click
3. Select "Open in Terminal"

**Method 3: From Start Menu**
1. Press `Windows + R`
2. Type: `powershell`
3. Press Enter
4. Navigate: `cd C:\path\to\your\project`

### Running Python Scripts

```powershell
# Run Python script
python script_name.py

# Run with specific Python version
python3 script_name.py
py -3 script_name.py

# Run and keep window open
python script_name.py
pause
```

---

## 📦 Recommended Windows Tools

### Essential:
- **VS Code** - Best code editor for Python
  - Download: https://code.visualstudio.com/
  - Extensions: Python, Pylance, GitLens
- **Git for Windows** - Includes Git Bash
  - Download: https://git-scm.com/download/win
- **Windows Terminal** - Better than default CMD
  - Install from Microsoft Store (Windows 10/11)

### Optional:
- **Python** (if not installed)
  - Download: https://www.python.org/downloads/
- **GitHub Desktop** - GUI for Git
  - Download: https://desktop.github.com/

---

## 🎓 Learning Resources

### PowerShell Basics:
- Microsoft Docs: https://learn.microsoft.com/en-us/powershell/
- PowerShell in a Month of Lunches (book)

### Python on Windows:
- Real Python Windows Guide: https://realpython.com/python-windows-machine-learning-setup/
- Python.org Windows FAQ: https://docs.python.org/3/faq/windows.html

---

## ✅ Checklist

After setup, you should have:

- [ ] V2.0 folder structure created
- [ ] `.env` file configured
- [ ] Python dependencies installed
- [ ] Git branch created
- [ ] Can import Python modules: `python -c "import config"`
- [ ] Ready to start migration!

---

## 🆘 Still Having Issues?

If you're stuck:

1. **Check you're in the right directory:**
   ```powershell
   Get-Location
   ```

2. **Verify Python is working:**
   ```powershell
   python --version
   pip --version
   ```

3. **Try the manual setup** instead of scripts

4. **Check the error message** - it usually tells you what's wrong

5. **Take screenshots** and review them - often the error message has the solution

---

**You've got this! The PowerShell script (Option 1) is the easiest way to get started on Windows. 🚀**
