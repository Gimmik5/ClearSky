# 🪟 WINDOWS USERS - START HERE!

## 📍 You Are Here

You're on Windows and want to set up ClearSky V2.0. Follow these simple steps:

---

## ⚡ Quick Start (5 minutes)

### Step 1: Open PowerShell in Your Project Folder

**How to do this:**
1. Open File Explorer
2. Navigate to your ClearSky project folder
3. Hold `Shift` and Right-click in empty space
4. Click "Open PowerShell window here"

**You should see something like:**
```
PS C:\Users\YourName\Projects\clearsky>
```

---

### Step 2: Run the Setup Script

**Copy and paste this into PowerShell:**
```powershell
.\setup_v2_structure.ps1
```

**If you get an error about execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_v2_structure.ps1
```

**✅ Success looks like:**
```
==============================================
  Structure Setup Complete! ✓
==============================================
```

---

### Step 3: Create Your Environment File

**Copy and paste:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Update these settings in Notepad:**
- `ESP32_IP=192.168.1.104` ← Your ESP32's IP address
- `DATABASE_PATH=./clearsky.db` ← Where to store data
- Save and close Notepad

---

### Step 4: Install Python Packages

**Copy and paste:**
```powershell
pip install -r requirements.txt
```

**If "pip not found":**
```powershell
python -m pip install -r requirements.txt
```

**⏳ This will take 2-3 minutes...**

---

### Step 5: Create Git Branch

**Copy and paste:**
```powershell
git checkout -b v2.0-restructure
git add .
git commit -m "feat: V2.0 folder structure"
```

---

## ✅ You're Done with Setup!

Your folder structure is now ready. You should see:

```
clearsky/
├── config/
├── data/
├── analysis/
├── hardware/
├── web/
├── utils/
├── tests/
├── scripts/
└── docs/
```

---

## 🎯 What's Next?

**Now you can start migrating your code:**

1. Open **MIGRATION_CHECKLIST.md** 
2. Start with **Phase 1: Config Migration** (easiest)
3. Follow the checklist step by step

**Each migration follows this pattern:**
1. Copy old file to new location
2. Update imports in the file
3. Test that it still works
4. Commit to Git
5. Move to next file

---

## 📚 Full Documentation

- **WINDOWS_SETUP_GUIDE.md** - Complete Windows guide (troubleshooting, tips)
- **README_V2_START_HERE.md** - Overall project guide
- **CLEARSKY_V2_ARCHITECTURE.md** - Why we're doing this
- **MIGRATION_CHECKLIST.md** - Step-by-step migration
- **QUICK_REFERENCE.md** - Code examples and import changes
- **TOOLS_GUIDE.md** - Technology deep dive

---

## 🐛 Common Issues

### "Cannot run scripts"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "pip not found"
```powershell
python -m pip install -r requirements.txt
```

### "Python not found"
Download from: https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation

### "Git not found"
Download from: https://git-scm.com/download/win

---

## ✅ Verification Checklist

After setup, verify everything works:

```powershell
# Check Python
python --version

# Check pip
pip --version

# Check Git
git --version

# Check folder structure
tree /F /A

# Test Python imports (after migration)
python -c "import config; print('✓ Config works')"
```

---

## 🆘 Need Help?

1. **First**: Read **WINDOWS_SETUP_GUIDE.md** (comprehensive troubleshooting)
2. **Stuck on setup?** Check you're in the right folder: `Get-Location`
3. **Stuck on migration?** Check **QUICK_REFERENCE.md** for import examples
4. **Error messages?** They usually tell you exactly what's wrong

---

## 🎉 You're Ready!

The hardest part (setup) is done. Now you can focus on migrating your code to the beautiful V2.0 structure.

**Remember:** 
- Migrate one module at a time
- Test after each change
- Commit frequently
- Don't panic - your V1 code still works!

**Good luck! 🚀**
