# Installation Guide

## Quick Install (Windows)

### Option 1: Automated Install (Recommended)
Run the PowerShell installation script:

```powershell
# From project directory
.\install_addin.ps1
```

The script will:
1. Detect your Fusion 360 add-ins directory
2. Offer symbolic link or file copy installation
3. Verify the installation
4. Provide next steps

### Option 2: Manual Install

1. **Locate Fusion Add-ins Directory**:
   ```
   %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns
   ```

2. **Create Symbolic Link** (Recommended):
   ```powershell
   # Run PowerShell as Administrator
   $fusionAddins = "$env:APPDATA\Autodesk\Autodesk Fusion 360\API\AddIns"
   New-Item -ItemType SymbolicLink -Path "$fusionAddins\FusionManufacturingPipeline" -Target "C:\Users\james.derrod\FusionExtension"
   ```

3. **Or Copy Files**:
   ```powershell
   $fusionAddins = "$env:APPDATA\Autodesk\Autodesk Fusion 360\API\AddIns"
   Copy-Item -Path "C:\Users\james.derrod\FusionExtension" -Destination "$fusionAddins\FusionManufacturingPipeline" -Recurse
   ```

## Quick Install (macOS)

### Manual Install

1. **Locate Fusion Add-ins Directory**:
   ```
   ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns
   ```

2. **Create Symbolic Link**:
   ```bash
   FUSION_ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
   ln -s "/path/to/FusionExtension" "$FUSION_ADDINS/FusionManufacturingPipeline"
   ```

3. **Or Copy Files**:
   ```bash
   FUSION_ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
   cp -r "/path/to/FusionExtension" "$FUSION_ADDINS/FusionManufacturingPipeline"
   ```

## Verify Installation

1. Navigate to Fusion add-ins directory
2. Check that `FusionManufacturingPipeline` folder exists
3. Verify these files are present:
   - `FusionManufacturingPipeline.manifest`
   - `src/addin.py`
   - `src/app.py`
   - `src/command_handler.py`
   - `schema.json`

## Load Add-in in Fusion 360

1. **Launch Fusion 360**

2. **Open Scripts and Add-Ins**:
   - Go to **UTILITIES** tab
   - Click **ADD-INS** button
   - Click **Scripts and Add-Ins**

3. **Find the Add-in**:
   - Switch to **Add-Ins** tab
   - Look for **FusionManufacturingPipeline** in the list

4. **Run the Add-in**:
   - Select **FusionManufacturingPipeline**
   - Click **Run** button
   - Confirm success message appears

5. **Verify Command**:
   - Go to **TOOLS** tab
   - Look for **ADD-INS** panel
   - Verify **Run Order** button is visible

## Troubleshooting

### Add-in Not Visible

**Problem**: Add-in doesn't appear in Scripts and Add-Ins dialog

**Solutions**:
- Verify manifest file exists: `FusionManufacturingPipeline.manifest`
- Check manifest file name matches folder name exactly
- Restart Fusion 360
- Check file permissions (must be readable)

### Import Errors

**Problem**: Error messages about "No module named 'src'"

**Solutions**:
- Verify `src/__init__.py` exists (should be created during Phase 1)
- Check directory structure matches expected layout
- Ensure all `.py` files are in correct locations

### Permission Denied (Windows Symbolic Link)

**Problem**: Cannot create symbolic link

**Solutions**:
- Run PowerShell as Administrator
- Use "Copy files" option instead of symbolic link
- Check Windows Developer Mode is enabled (Settings → Update & Security → For Developers)

### Manifest Parse Error

**Problem**: Fusion reports manifest file error

**Solutions**:
- Verify manifest JSON syntax is valid
- Check for extra commas or missing quotes
- Compare against original manifest file

## Uninstall

### Windows
```powershell
$fusionAddins = "$env:APPDATA\Autodesk\Autodesk Fusion 360\API\AddIns"
Remove-Item "$fusionAddins\FusionManufacturingPipeline" -Recurse -Force
```

### macOS
```bash
FUSION_ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
rm -rf "$FUSION_ADDINS/FusionManufacturingPipeline"
```

## Next Steps

After successful installation:
1. Follow the testing guide: `docs/PHASE1_TESTING.md`
2. Test with sample order: `samples/sample_order.json`
3. Review logs in `logs/` directory after running
4. Report any issues or move to Phase 2 development

## Development Mode

For active development, use symbolic link installation. This allows:
- ✅ Edit code without reinstalling
- ✅ Reload add-in to see changes (Stop → Run)
- ✅ View logs in project `logs/` directory
- ✅ Version control integration

For production use, file copy is more stable.
