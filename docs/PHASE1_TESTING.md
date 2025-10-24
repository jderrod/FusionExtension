# Phase 1 Testing Guide

## Manual Testing in Fusion 360

Phase 1 implements the add-in skeleton with command registration and JSON validation. Follow this guide to test the add-in in Fusion 360.

## Prerequisites

1. ✅ Fusion 360 Desktop installed
2. ✅ Phase 0 completed (schema and validator working)
3. ✅ Sample order file exists: `samples/sample_order.json`

## Installation Steps

### 1. Copy Add-in to Fusion

Copy the entire project to Fusion's add-in directory:

**Windows**:
```powershell
# Target directory
$fusionAddins = "$env:APPDATA\Autodesk\Autodesk Fusion 360\API\AddIns"

# Create symbolic link (recommended) or copy files
New-Item -ItemType SymbolicLink -Path "$fusionAddins\FusionManufacturingPipeline" -Target "C:\Users\james.derrod\FusionExtension"

# Or copy directly
Copy-Item -Path "C:\Users\james.derrod\FusionExtension" -Destination "$fusionAddins\FusionManufacturingPipeline" -Recurse
```

**macOS**:
```bash
# Target directory
FUSION_ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"

# Create symbolic link (recommended)
ln -s "/path/to/FusionExtension" "$FUSION_ADDINS/FusionManufacturingPipeline"
```

### 2. Verify Directory Structure

The add-in directory should contain:
```
FusionManufacturingPipeline/
├── FusionManufacturingPipeline.manifest
├── schema.json
├── src/
│   ├── addin.py          # Entry point
│   ├── app.py            # Application logic
│   ├── command_handler.py # Command handlers
│   ├── validator.py       # Schema validation
│   └── logger.py          # Logging utilities
└── samples/
    └── sample_order.json
```

## Testing Procedure

### Test 1: Load Add-in

**Steps**:
1. Launch Fusion 360
2. Go to **UTILITIES** tab → **ADD-INS** button
3. Click **Scripts and Add-Ins**
4. In the **Add-Ins** tab, find **FusionManufacturingPipeline**
5. Click **Run**

**Expected Result**:
- ✅ Add-in loads without errors
- ✅ Message box appears: "Fusion Manufacturing Pipeline loaded successfully"
- ✅ Message mentions "Run Order" command in TOOLS tab

**If Failed**:
- Check Fusion's Text Commands window for error messages
- Verify manifest file is correctly named and formatted
- Ensure all Python files have correct imports

### Test 2: Locate Command

**Steps**:
1. After add-in loads, go to **TOOLS** tab
2. Look for **ADD-INS** panel
3. Find **Run Order** button

**Expected Result**:
- ✅ "Run Order" button is visible
- ✅ Tooltip shows: "Load and process a JSON manufacturing order"

**If Failed**:
- Check if add-in loaded successfully in Test 1
- Verify WORKSPACE_ID and PANEL_ID in `app.py` are correct
- Look for registration errors in logs

### Test 3: Execute Command (No File)

**Steps**:
1. Click **Run Order** button
2. Observe the dialog that appears
3. Do NOT select a file yet
4. Try to click **OK**

**Expected Result**:
- ✅ Dialog opens with three sections:
  - Order File (showing "No file selected")
  - Browse... button
  - Validation Status (showing "Please select an order file")
- ✅ **OK** button is disabled (grayed out)

**If Failed**:
- Check command_handler.py for input creation errors
- Review validateInputs handler logic

### Test 4: Browse for File

**Steps**:
1. In the Run Order dialog, click **Browse...**
2. Navigate to `samples/sample_order.json`
3. Select the file and click **Open**

**Expected Result**:
- ✅ File dialog opens
- ✅ Initial directory is the samples folder
- ✅ Filter shows "JSON Files (*.json)"
- ✅ After selection, Order File field updates with file path
- ✅ Validation Status shows: "✓ Valid order file" (in green)
- ✅ **OK** button is now enabled

**If Failed**:
- Check if samples/sample_order.json exists
- Verify validator.py is working (run unit tests)
- Check InputChangedHandler logic

### Test 5: Validate Invalid File

**Steps**:
1. Create a test file `test_invalid.json` with invalid content:
   ```json
   {
     "version": "1.0.0",
     "orderId": "",
     "components": []
   }
   ```
2. In Run Order dialog, click **Browse...**
3. Select `test_invalid.json`

**Expected Result**:
- ✅ Validation Status shows: "✗ Validation errors:"
- ✅ Lists specific errors (e.g., "orderId cannot be empty", "components array must contain at least 1 item")
- ✅ Text appears in red
- ✅ **OK** button remains disabled

**If Failed**:
- Verify validator.py correctly identifies errors
- Run: `python src/validator.py test_invalid.json` to test validator

### Test 6: Execute with Valid File

**Steps**:
1. In Run Order dialog, select valid `samples/sample_order.json`
2. Verify validation shows "✓ Valid order file"
3. Click **OK**

**Expected Result**:
- ✅ Information message box appears with:
  - File path
  - "Phase 1 Complete: Add-in skeleton ready"
  - "Phase 2 will implement parameter application"
- ✅ No errors in Text Commands window
- ✅ Log file created in `logs/` directory

**If Failed**:
- Check ExecuteHandler in command_handler.py
- Review logs directory for error details

### Test 7: Verify Logging

**Steps**:
1. Navigate to project's `logs/` directory
2. Find the most recent log file (format: `pipeline_YYYYMMDD_HHMMSS.log`)
3. Open the log file

**Expected Result**:
- ✅ Log file exists and is readable
- ✅ Contains initialization message: "Logger initialized"
- ✅ Contains timestamps for all operations

**If Failed**:
- Check if logs directory exists
- Verify logger.py initialization logic
- Check file permissions

### Test 8: Unload Add-in

**Steps**:
1. Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins**
2. Select **FusionManufacturingPipeline**
3. Click **Stop**

**Expected Result**:
- ✅ Message box: "Fusion Manufacturing Pipeline unloaded"
- ✅ "Run Order" command disappears from TOOLS tab
- ✅ No errors in Text Commands window

**If Failed**:
- Check stop() function in addin.py
- Verify cleanup logic in app.py unregister_command()

## Test Matrix

| Test | Feature | Status |
|------|---------|--------|
| 1 | Add-in loading | ⬜ |
| 2 | Command registration | ⬜ |
| 3 | Dialog inputs | ⬜ |
| 4 | File selection | ⬜ |
| 5 | Validation (invalid) | ⬜ |
| 6 | Validation (valid) | ⬜ |
| 7 | Logging | ⬜ |
| 8 | Add-in unloading | ⬜ |

## Common Issues

### Issue: Add-in Not Visible

**Symptoms**: Add-in doesn't appear in Scripts and Add-Ins dialog

**Solutions**:
1. Verify manifest file name matches directory name
2. Check manifest JSON syntax
3. Restart Fusion 360
4. Check `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns` directory

### Issue: Module Import Errors

**Symptoms**: Error messages about "No module named 'src'"

**Solutions**:
1. Verify directory structure is correct
2. Check that `src/__init__.py` exists (create empty file if needed)
3. Ensure all imports use `from src import ...` format

### Issue: Command Not Appearing

**Symptoms**: Add-in loads but Run Order button doesn't appear

**Solutions**:
1. Check Text Commands window for registration errors
2. Verify WORKSPACE_ID and PANEL_ID in app.py
3. Try reloading the add-in (Stop → Run)

### Issue: Validation Fails for Valid File

**Symptoms**: sample_order.json shows validation errors

**Solutions**:
1. Run validator unit tests: `pytest tests/test_validator.py`
2. Test validator CLI: `python src/validator.py samples/sample_order.json`
3. Check schema.json is in repo root
4. Verify file paths in sample_order.json use correct format

### Issue: File Dialog Doesn't Open

**Symptoms**: Clicking Browse... does nothing

**Solutions**:
1. Check for errors in Text Commands window
2. Verify InputChangedHandler is properly connected
3. Check file dialog creation code in command_handler.py

## Debugging Tips

### Enable Verbose Logging

Add debug statements in code:
```python
app_obj = adsk.core.Application.get()
ui = app_obj.userInterface
ui.messageBox(f'Debug: {variable_value}')
```

### Check Text Commands Window

1. In Fusion, go to **UTILITIES** → **ADD-INS** → **Text Commands**
2. This shows console output and error messages
3. Look for Python exceptions and stack traces

### Review Log Files

Log files in `logs/` directory contain detailed operation logs:
```powershell
# View latest log (PowerShell)
Get-Content (Get-ChildItem logs\pipeline_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

### Test Components Individually

Test validator independently:
```bash
python src/validator.py samples/sample_order.json
```

## Success Criteria

Phase 1 is considered complete when:
- ✅ All 8 tests pass
- ✅ Add-in loads and unloads cleanly
- ✅ Command appears in UI
- ✅ File selection works
- ✅ Validation works correctly (valid and invalid files)
- ✅ Logging works
- ✅ No errors in normal operation

## Next Steps

Once Phase 1 testing is complete:
1. Document any issues encountered
2. Update PHASE1_SUMMARY.md with test results
3. Proceed to **Phase 2: Parameter Application**
4. Implement actual parameter updates in Fusion models

## Test Report Template

```
# Phase 1 Test Report

**Tester**: [Your Name]
**Date**: [Date]
**Fusion Version**: [Version]

## Test Results

| Test # | Result | Notes |
|--------|--------|-------|
| 1 | PASS/FAIL | |
| 2 | PASS/FAIL | |
| 3 | PASS/FAIL | |
| 4 | PASS/FAIL | |
| 5 | PASS/FAIL | |
| 6 | PASS/FAIL | |
| 7 | PASS/FAIL | |
| 8 | PASS/FAIL | |

## Issues Found

[List any issues]

## Recommendations

[Any recommendations for improvements]
```
