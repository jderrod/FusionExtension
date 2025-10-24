# Install Fusion 360 Manufacturing Pipeline Add-in
# PowerShell script for Windows

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fusion Manufacturing Pipeline Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project root (where this script is located)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Project location: $ProjectRoot" -ForegroundColor Yellow

# Get Fusion add-ins directory
$FusionAddins = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"

if (-not (Test-Path $FusionAddins)) {
    Write-Host "ERROR: Fusion 360 add-ins directory not found!" -ForegroundColor Red
    Write-Host "Expected: $FusionAddins" -ForegroundColor Red
    Write-Host "" 
    Write-Host "Please install Fusion 360 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Fusion add-ins directory: $FusionAddins" -ForegroundColor Yellow
Write-Host ""

# Target add-in directory
$TargetDir = Join-Path $FusionAddins "FusionManufacturingPipeline"

# Check if already installed
if (Test-Path $TargetDir) {
    Write-Host "Add-in already installed at: $TargetDir" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to reinstall? (y/n)"
    
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Removing existing installation..." -ForegroundColor Yellow
    Remove-Item $TargetDir -Recurse -Force
}

# Ask for installation method
Write-Host "Choose installation method:" -ForegroundColor Cyan
Write-Host "  1. Symbolic link (recommended - allows live editing)"
Write-Host "  2. Copy files (standalone - no live updates)"
Write-Host ""
$method = Read-Host "Enter choice (1 or 2)"

if ($method -eq '1') {
    # Create symbolic link
    Write-Host ""
    Write-Host "Creating symbolic link..." -ForegroundColor Yellow
    
    try {
        # Verify source exists
        if (-not (Test-Path $ProjectRoot)) {
            throw "Source directory does not exist: $ProjectRoot"
        }
        
        # Debug output
        Write-Host "  Source: $ProjectRoot" -ForegroundColor Gray
        Write-Host "  Target: $TargetDir" -ForegroundColor Gray
        Write-Host ""
        
        # Create the symbolic link using cmd mklink (more reliable on Windows)
        $mklinkCmd = "cmd /c mklink /D `"$TargetDir`" `"$ProjectRoot`""
        $result = Invoke-Expression $mklinkCmd 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "mklink failed: $result"
        }
        
        Write-Host "Success: Symbolic link created!" -ForegroundColor Green
        Write-Host "  Changes to your project will be reflected immediately in Fusion." -ForegroundColor Gray
    }
    catch {
        Write-Host "ERROR: Failed to create symbolic link!" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Try one of these solutions:" -ForegroundColor Yellow
        Write-Host "  1. Ensure you're running PowerShell as Administrator"
        Write-Host "  2. Enable Developer Mode in Windows Settings"
        Write-Host "  3. Choose option 2 (copy files) instead"
        exit 1
    }
}
elseif ($method -eq '2') {
    # Copy files
    Write-Host ""
    Write-Host "Copying files..." -ForegroundColor Yellow
    
    try {
        Copy-Item -Path $ProjectRoot -Destination $TargetDir -Recurse -Force
        
        # Remove unnecessary files from copy
        $itemsToRemove = @(
            ".git",
            ".pytest_cache",
            "__pycache__",
            "logs",
            "*.pyc",
            ".gitignore"
        )
        
        foreach ($item in $itemsToRemove) {
            $fullPath = Join-Path $TargetDir $item
            if (Test-Path $fullPath) {
                Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        
        Write-Host "Success: Files copied!" -ForegroundColor Green
        Write-Host "  Note: Changes to your project will NOT be reflected automatically." -ForegroundColor Gray
        Write-Host "  You will need to reinstall after making changes." -ForegroundColor Gray
    }
    catch {
        Write-Host "ERROR: Failed to copy files!" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Invalid choice. Installation cancelled." -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow

$manifestPath = Join-Path $TargetDir "FusionManufacturingPipeline.manifest"
if (Test-Path $manifestPath) {
    Write-Host "  Manifest file found" -ForegroundColor Green
}
else {
    Write-Host "  ERROR: Manifest file missing!" -ForegroundColor Red
    exit 1
}

$addinPath = Join-Path $TargetDir "src" | Join-Path -ChildPath "addin.py"
if (Test-Path $addinPath) {
    Write-Host "  Add-in entry point found" -ForegroundColor Green
}
else {
    Write-Host "  ERROR: Add-in entry point missing!" -ForegroundColor Red
    exit 1
}

# Success!
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Launch Fusion 360"
Write-Host "  2. Go to UTILITIES, then ADD-INS, then Scripts and Add-Ins"
Write-Host "  3. In the Add-Ins tab, find FusionManufacturingPipeline"
Write-Host "  4. Click Run to start the add-in"
Write-Host "  5. Look for Run Order in TOOLS under ADD-INS"
Write-Host ""
Write-Host "For testing instructions, see docs/PHASE1_TESTING.md" -ForegroundColor Yellow
Write-Host ""
