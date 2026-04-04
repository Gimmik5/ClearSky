# ClearSky V2.0 - Automated Folder Structure Setup (PowerShell for Windows)
# Run this script from your project root directory

$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  ClearSky V2.0 Structure Setup (Windows)" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------------------------
# CREATE MAIN DIRECTORIES
# ---------------------------------------------------------------------------------------------
Write-Host "Creating main directories..." -ForegroundColor Blue

$directories = @(
    "config",
    "data\migrations",
    "data\storage",
    "analysis\ml\models",
    "analysis\ml\training",
    "hardware",
    "web\routes",
    "web\templates\gallery",
    "web\templates\viewer",
    "web\static\css",
    "web\static\js",
    "web\static\img",
    "web\components",
    "utils",
    "tests\test_analysis",
    "tests\test_data",
    "tests\test_hardware",
    "tests\test_web",
    "scripts",
    "docs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[+] Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "[o] Exists:  $dir" -ForegroundColor Yellow
    }
}

Write-Host ""

# ---------------------------------------------------------------------------------------------
# CREATE __init__.py FILES
# ---------------------------------------------------------------------------------------------
Write-Host "Creating Python package files..." -ForegroundColor Blue

$initFiles = @(
    "config\__init__.py",
    "data\__init__.py",
    "data\migrations\__init__.py",
    "data\storage\__init__.py",
    "analysis\__init__.py",
    "analysis\ml\__init__.py",
    "hardware\__init__.py",
    "web\__init__.py",
    "web\routes\__init__.py",
    "web\components\__init__.py",
    "utils\__init__.py",
    "tests\__init__.py",
    "tests\test_analysis\__init__.py",
    "tests\test_data\__init__.py",
    "tests\test_hardware\__init__.py",
    "tests\test_web\__init__.py"
)

foreach ($file in $initFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "[+] Created: $file" -ForegroundColor Green
    } else {
        Write-Host "[o] Exists:  $file" -ForegroundColor Yellow
    }
}

Write-Host ""

# ---------------------------------------------------------------------------------------------
# CREATE MODULE PLACEHOLDER FILES
# ---------------------------------------------------------------------------------------------
Write-Host "Creating module placeholder files..." -ForegroundColor Blue

$moduleFiles = @(
    "config\settings.py",
    "config\database_config.py",
    "config\hardware_config.py",
    "config\analysis_config.py",
    "data\models.py",
    "data\schema.py",
    "data\operations.py",
    "data\manager.py",
    "analysis\core.py",
    "analysis\brightness.py",
    "analysis\color.py",
    "analysis\sky_features.py",
    "analysis\ml\inference.py",
    "hardware\poller.py",
    "hardware\connection.py",
    "hardware\protocol.py",
    "web\app.py",
    "web\routes\main_routes.py",
    "web\routes\api_routes.py",
    "web\routes\gallery_routes.py",
    "web\routes\viewer_routes.py",
    "utils\logger.py",
    "utils\shutdown.py",
    "utils\server_utils.py",
    "utils\diagnostics.py",
    "scripts\init_database.py",
    "scripts\diagnostic_queue.py",
    "scripts\export_data.py"
)

foreach ($file in $moduleFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "[+] Created: $file" -ForegroundColor Green
    } else {
        Write-Host "[o] Exists:  $file" -ForegroundColor Yellow
    }
}

Write-Host ""

# ---------------------------------------------------------------------------------------------
# CREATE .env.example
# ---------------------------------------------------------------------------------------------
Write-Host "Creating configuration files..." -ForegroundColor Blue

if (-not (Test-Path ".env.example")) {
    $envContent = @"
# ClearSky V2.0 Configuration

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8080

# Database Configuration
DATABASE_PATH=./clearsky.db
DATABASE_BACKUP_PATH=./backups/

# ESP32 Configuration
ESP32_IP=192.168.1.104
ESP32_PORT=80
POLL_INTERVAL_SECONDS=10
REQUEST_TIMEOUT=15

# Analysis Configuration
ENABLE_BRIGHTNESS_ANALYSIS=True
ENABLE_COLOR_ANALYSIS=True
ENABLE_SKY_FEATURES=True

# Image Storage
IMAGE_DIR=./images/
MAX_IMAGE_AGE_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/clearsky.log
"@
    Set-Content -Path ".env.example" -Value $envContent
    Write-Host "[+] Created: .env.example" -ForegroundColor Green
}

# -------------------------------------------------------------------------------------
# CREATE requirements.txt
# -----------------------------------------------------------------------------------

if (-not (Test-Path "requirements.txt")) {
    $requirementsContent = @"
# ClearSky V2.0 Dependencies
Flask==3.0.0
flask-cors==4.0.0
waitress==2.1.2
SQLAlchemy==2.0.23
alembic==1.13.1
Pillow==10.1.0
opencv-python==4.8.1.78
numpy==1.26.2
pandas==2.1.4
scikit-learn==1.3.2
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
"@
    Set-Content -Path "requirements.txt" -Value $requirementsContent
    Write-Host "[+] Created: requirements.txt" -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# CREATE .gitignore
# -------------------------------------------------------------------------------------

if (-not (Test-Path ".gitignore")) {
    $gitignoreContent = @"
__pycache__/
*.py[cod]
venv/
.env
*.db
*.log
images/
"@
    Set-Content -Path ".gitignore" -Value $gitignoreContent
    Write-Host "[+] Created: .gitignore" -ForegroundColor Green
}

Write-Host ""

# -------------------------------------------------
# CREATE DOCUMENTATION STUBS
# --------------------------------------------------
Write-Host "Creating documentation stubs..." -ForegroundColor Blue

$docFiles = @(
    "docs\API.md",
    "docs\ARCHITECTURE.md",
    "docs\DEPLOYMENT.md",
    "docs\TROUBLESHOOTING.md"
)

foreach ($file in $docFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "[+] Created: $file" -ForegroundColor Green
    }
}

Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Structure Setup Complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green