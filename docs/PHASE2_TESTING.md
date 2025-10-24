# Phase 2 Testing Guide: Parameter Application

## Overview

Phase 2 implements parameter application - reading Fusion 360 user parameters and updating them based on JSON order values.

## Prerequisites

1. ✅ Phase 1 complete and working
2. ✅ Fusion 360 design file with user parameters
3. ✅ Sample order JSON with parameter values

## Testing Prerequisites

### Required: Door Panel Fusion File

You need a Fusion 360 design file (.f3d) with the following user parameters defined:

**Required Parameters (from FusionModelParametersToChange.csv):**
- `door_panel_height` - Panel height with units (e.g., "2100 mm")
- `door_panel_width` - Panel width with units (e.g., "900 mm")
- `door_clearance_height` - Height clearance (e.g., "10 mm")
- `door_clearance_width` - Width clearance (e.g., "10 mm")
- `door_hinging` - Hinging side (0 or 1)
- `door_swinging` - Swing direction (0 or 1)
- `door_wall_keep_latching` - Wall keep on latch side (0 or 1)

### Update sample_order.json

Update the `fusionFile` path in `samples/sample_order.json` to point to your door panel model:

```json
{
  "version": "1.0.0",
  "orderId": "TEST_PHASE2_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": [
    {
      "componentId": "DoorPanel_001",
      "fusionFile": "C:/Path/To/Your/DoorPanel.f3d",
      "parameters": {
        "door_panel_height": "2100 mm",
        "door_panel_width": "900 mm",
        "door_clearance_height": "10 mm",
        "door_clearance_width": "10 mm",
        "door_hinging": "0",
        "door_swinging": "1",
        "door_wall_keep_latching": "1"
      }
    }
  ]
}
```

## Test Procedure

### Test 1: Verify Parameter Manager

**Objective**: Confirm parameter reading works

**Steps**:
1. Open your door panel model in Fusion 360
2. Go to **MODIFY → Change Parameters**
3. Note the current values of the 7 door parameters
4. Close the parameters dialog

### Test 2: Run Order with Parameters

**Steps**:
1. Ensure `samples/sample_order.json` points to your door panel .f3d file
2. In Fusion, go to **SOLID → CREATE (PCB)** → **Run Order**
3. Watch for progress messages:
   - "Order file validated successfully"
   - "Processing component 1 of 1: DoorPanel_001"
   - Individual parameter update messages
4. Click OK on each message

**Expected Results**:
- ✅ Dialog shows "Processing component 1 of 1"
- ✅ Dialog shows successful parameter updates
- ✅ Final message: "Order Processing Complete!"
- ✅ Message shows: "Successfully updated 7 parameter(s)"

### Test 3: Verify Parameters Changed

**Steps**:
1. In Fusion, go to **MODIFY → Change Parameters**
2. Check the values of the 7 door parameters
3. Compare to values in `sample_order.json`

**Expected Results**:
- ✅ All parameters match the JSON values
- ✅ Parameters with units preserved (e.g., "2100 mm")
- ✅ Numeric parameters updated correctly

### Test 4: Check Logs

**Steps**:
```powershell
# View the latest log file
Get-Content (Get-ChildItem C:\Users\james.derrod\FusionExtension\logs\pipeline_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 30
```

**Expected Log Entries**:
```
2024-01-15 10:30:00 - INFO - Loading order from: C:\...\sample_order.json
2024-01-15 10:30:01 - INFO - Processing order: TEST_PHASE2_001 with 1 component(s)
2024-01-15 10:30:01 - INFO - Processing component 1/1: DoorPanel_001
2024-01-15 10:30:01 - INFO -   Fusion file: C:\...\DoorPanel.f3d
2024-01-15 10:30:01 - INFO -   Parameters to apply: 7
2024-01-15 10:30:02 - INFO - Applying parameters to DoorPanel_001
2024-01-15 10:30:02 - INFO -   ✓ Updated 'door_panel_height' from '2000 mm' to '2100 mm'
2024-01-15 10:30:02 - INFO -   ✓ Updated 'door_panel_width' from '850 mm' to '900 mm'
... (more parameter updates)
```

### Test 5: Multiple Updates

**Objective**: Test updating same model multiple times

**Steps**:
1. Note current parameter values
2. Run the order (Run Order command)
3. Verify parameters changed
4. Edit `sample_order.json` with different values
5. Run the order again
6. Verify parameters changed to new values

**Expected Results**:
- ✅ Parameters update correctly each time
- ✅ No errors on subsequent runs
- ✅ Logs show both old and new values

### Test 6: Error Handling - Missing Parameter

**Objective**: Test error handling for invalid parameters

**Steps**:
1. Edit `sample_order.json` to include a non-existent parameter:
   ```json
   "parameters": {
     "door_panel_height": "2100 mm",
     "nonexistent_param": "123"
   }
   ```
2. Run the order

**Expected Results**:
- ✅ Error message appears
- ✅ Message indicates which parameter failed
- ✅ Message: "Parameter 'nonexistent_param' not found in model"

### Test 7: Error Handling - Missing File

**Objective**: Test error handling for missing Fusion file

**Steps**:
1. Edit `sample_order.json` with invalid file path:
   ```json
   "fusionFile": "C:/NonExistent/File.f3d"
   ```
2. Run the order

**Expected Results**:
- ✅ Error message appears
- ✅ Message: "Failed to open document"
- ✅ No crash or silent failure

## Troubleshooting

### Issue: "No design found in document"

**Cause**: The .f3d file might be a CAM-only file or corrupted

**Solution**:
- Ensure the file has a design workspace
- Try opening the file manually in Fusion first
- Check file isn't corrupted

### Issue: "Parameter 'X' not found in model"

**Cause**: Parameter doesn't exist in the Fusion model

**Solutions**:
1. Open the model in Fusion
2. Go to MODIFY → Change Parameters
3. Verify the parameter name matches exactly (case-sensitive)
4. Add missing parameters if needed

### Issue: Parameters don't update

**Cause**: Parameter expression format might be invalid

**Solutions**:
- Ensure units are included for dimension parameters (e.g., "100 mm" not "100")
- For numeric parameters without units, use plain numbers (e.g., "0" or "1")
- Check log file for detailed error messages

### Issue: Fusion file won't open

**Cause**: File path issues or file in use

**Solutions**:
- Use absolute paths in JSON (not relative)
- Use forward slashes or double backslashes: `C:/Path/File.f3d` or `C:\\Path\\File.f3d`
- Close the file in Fusion before running the order
- Check file permissions

## Success Criteria

Phase 2 is complete when:
- ✅ All 7 tests pass
- ✅ Parameters update correctly from JSON
- ✅ Logs show detailed parameter changes
- ✅ Error handling works for invalid inputs
- ✅ Multiple runs work without issues

## Next: Phase 3

Once Phase 2 testing is complete, proceed to **Phase 3: CAM Toolpath Regeneration**.

Phase 3 will add:
- CAM workspace activation
- Toolpath regeneration after parameter changes
- Setup filtering based on JSON configuration

## Test Report Template

```
# Phase 2 Test Report

**Tester**: [Your Name]
**Date**: [Date]
**Fusion Version**: [Version]
**Model**: [Path to door panel .f3d]

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

## Parameter Update Examples

| Parameter | Old Value | New Value | Status |
|-----------|-----------|-----------|--------|
| door_panel_height | | | |
| door_panel_width | | | |
| ... | | | |

## Issues Found

[List any issues]

## Log File Location

[Path to log file with timestamps]
```
