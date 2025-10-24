# Phase 3 Testing Guide: CAM Toolpath Regeneration

## Overview

Phase 3 implements CAM toolpath regeneration after parameter updates. When parameters change, all toolpaths are automatically regenerated to reflect the new geometry.

## Prerequisites

1. ✅ Phase 1 & 2 complete and working
2. ✅ Fusion 360 design file with CAM setups configured
3. ✅ CAM setups must be: **"hinge_side"** and **"routing_side"**

## CAM Setup Requirements

### Your Model Must Have CAM Data

The door panel model must have CAM workspace configured with:
- **Setup 1 Name**: "hinge_side"
- **Setup 2 Name**: "routing_side"
- Operations defined in each setup
- Tool library configured
- Stock properly defined

**To check:**
1. Open your model in Fusion 360
2. Switch to **MANUFACTURE** workspace (top menu)
3. Verify you see two setups: "hinge_side" and "routing_side"
4. Verify each setup has operations (toolpaths)

## Test Procedure

### Test 1: Verify CAM Setups Exist

**Objective**: Confirm CAM data is present

**Steps**:
1. Open `F360MT - PartitionDoor(1).f3d` in Fusion
2. Switch to **MANUFACTURE** workspace
3. Check the browser panel on left
4. Verify two setups exist: "hinge_side" and "routing_side"

**Expected**:
- ✅ Both setups visible
- ✅ Each setup has operations underneath
- ✅ Setups are not suppressed

### Test 2: Run Full Order (Parameters + CAM)

**Objective**: Test complete workflow with toolpath regeneration

**Steps**:
1. Ensure model is open with CAM setups configured
2. In Fusion: **SOLID → CREATE (PCB) → Run Order**
3. Watch for progress messages:
   - Current parameters listed
   - Parameters updated (7 parameters)
   - "Found 2 CAM setup(s): hinge_side, routing_side"
   - "Regenerating toolpaths..."
   - Progress for each setup

**Expected Results**:
- ✅ Dialog: "Found 28 user parameters in current model"
- ✅ Dialog: "Parameters Updated" with 7 parameter updates
- ✅ Dialog: "Found 2 CAM setup(s): • hinge_side • routing_side"
- ✅ Dialog: "Regenerating toolpaths for setup: hinge_side"
- ✅ Dialog: "Regenerating toolpaths for setup: routing_side"
- ✅ Dialog: "Component Complete! ✓ Updated 7 parameter(s) ✓ Regenerated 2 CAM setup(s)"
- ✅ Final: "Order Processing Complete!"

### Test 3: Verify Toolpaths Updated

**Objective**: Confirm toolpaths reflect new parameters

**Steps**:
1. Stay in **MANUFACTURE** workspace
2. Check each setup's operations
3. Look at toolpaths in graphics window

**Expected**:
- ✅ Toolpaths are regenerated (not showing old geometry)
- ✅ Tool motions match new door size (84" x 30" vs 96" x 50")
- ✅ No errors in operations
- ✅ Estimated time may have changed

### Test 4: Check Logs

**Steps**:
```powershell
Get-Content (Get-ChildItem C:\Users\james.derrod\FusionExtension\logs\pipeline_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 50
```

**Expected Log Entries**:
```
INFO - Processing component 1/1: door-panel-001
INFO - Applying parameters to door-panel-001
INFO - ✓ Updated 'component_height' from '96 in' to '84 in'
... (more parameter updates)
INFO - Parameter updates complete, starting CAM regeneration
INFO - Activating CAM workspace
INFO - CAM workspace activated
INFO - Found 2 CAM setup(s): hinge_side, routing_side
INFO - Regenerating toolpaths for all setups
INFO - Setup "hinge_side": Toolpaths regenerated successfully
INFO - Setup "routing_side": Toolpaths regenerated successfully
INFO - All operations complete
```

### Test 5: Multiple Runs

**Objective**: Test that regeneration works repeatedly

**Steps**:
1. Note current toolpath geometry
2. Edit `sample_order.json` with different values:
   ```json
   "component_height": "72 in",
   "component_width": "24 in"
   ```
3. Run order again
4. Check toolpaths updated to new size

**Expected**:
- ✅ Parameters update to new values
- ✅ Toolpaths regenerate successfully
- ✅ Geometry reflects 72" x 24" dimensions
- ✅ No errors on subsequent runs

### Test 6: Error Handling - No CAM Data

**Objective**: Test error handling when CAM data missing

**Steps**:
1. Create a simple Fusion design with user parameters but NO CAM data
2. Update `sample_order.json` to point to this file
3. Run order

**Expected**:
- ✅ Parameters update successfully
- ✅ Error message: "No CAM data found in document"
- ✅ Order marked as FAILED
- ✅ Logs show the error

### Test 7: Error Handling - Wrong Setup Names

**Objective**: Verify it finds your specific setup names

**Note**: Phase 3 regenerates ALL setups, so this test verifies it finds "hinge_side" and "routing_side" specifically.

**Steps**:
1. Run order with normal door panel model
2. Check dialog shows both setup names

**Expected**:
- ✅ Dialog lists: "hinge_side" and "routing_side"
- ✅ Both setups regenerated
- ✅ Success message

## Troubleshooting

### Issue: "No CAM data found in document"

**Cause**: Model doesn't have CAM workspace configured

**Solutions**:
1. Switch to MANUFACTURE workspace in Fusion
2. Create CAM setups if they don't exist
3. Ensure setups are named "hinge_side" and "routing_side"
4. Run at least one toolpath generation manually first

### Issue: "No CAM setups found in document"

**Cause**: CAM workspace exists but no setups created

**Solution**:
1. In MANUFACTURE workspace, create setups
2. Add operations to each setup
3. Generate toolpaths at least once manually

### Issue: Toolpath generation hangs

**Cause**: Large model or complex toolpaths

**Solutions**:
- Be patient - toolpath generation can take time
- Check Fusion isn't waiting for user input
- Look for dialog boxes in background
- Check task manager - Fusion should be using CPU

### Issue: "Toolpath regeneration failed"

**Cause**: Invalid operations or tool issues

**Solutions**:
1. Manually generate toolpaths in MANUFACTURE workspace
2. Fix any errors shown in Fusion
3. Verify tools are valid in tool library
4. Check stock is properly defined
5. Ensure operations are not suppressed

### Issue: Toolpaths don't match new geometry

**Cause**: Toolpath generation completed but didn't update properly

**Solutions**:
1. Manually regenerate in MANUFACTURE workspace to compare
2. Check if parameters actually changed (verify in Change Parameters)
3. Try closing and reopening the model
4. Check model dependencies are updating correctly

## Expected Workflow

```
User clicks "Run Order"
  ↓
1. Load order JSON
  ↓
2. Show current parameters
  ↓
3. Update 7 parameters (84 in, 30 in, etc.)
  ↓
4. Show "Parameters Updated" dialog
  ↓
5. Activate CAM workspace
  ↓
6. List setups: "hinge_side", "routing_side"
  ↓
7. Show "Found 2 CAM setup(s)" dialog
  ↓
8. Generate toolpaths for hinge_side
  ↓
9. Generate toolpaths for routing_side
  ↓
10. Show "Component Complete" with summary
  ↓
11. Return to DESIGN workspace
  ↓
Success!
```

## Success Criteria

Phase 3 is complete when:
- ✅ All 7 tests pass
- ✅ Toolpaths regenerate successfully after parameter changes
- ✅ Both "hinge_side" and "routing_side" setups updated
- ✅ Logs show detailed CAM operations
- ✅ Error handling works for missing CAM data
- ✅ Multiple runs work without issues
- ✅ Toolpaths reflect new geometry accurately

## Performance Notes

**Typical Timing**:
- Parameter updates: < 1 second
- CAM workspace activation: 1-2 seconds
- Toolpath regeneration: 10-60 seconds per setup (depends on complexity)
- Total time: 30-120 seconds for complete order

**Progress Indicators**:
- Multiple dialog boxes show progress
- Fusion may appear busy during toolpath generation
- CPU usage will be high during regeneration

## Next: Phase 4

Once Phase 3 testing is complete, proceed to **Phase 4: Post Processing & G-code Generation**.

Phase 4 will add:
- Post processor execution
- G-code file generation
- Output file management
- Multi-setup output handling

## Test Report Template

```
# Phase 3 Test Report

**Tester**: [Your Name]
**Date**: [Date]
**Fusion Version**: [Version]
**Model**: F360MT - PartitionDoor(1).f3d
**CAM Setups**: hinge_side, routing_side

## Test Results

| Test # | Result | Notes |
|--------|--------|-------|
| 1 | PASS/FAIL | CAM setups exist |
| 2 | PASS/FAIL | Full order run |
| 3 | PASS/FAIL | Toolpaths updated |
| 4 | PASS/FAIL | Logs complete |
| 5 | PASS/FAIL | Multiple runs |
| 6 | PASS/FAIL | Error: no CAM |
| 7 | PASS/FAIL | Setup names |

## Toolpath Regeneration

| Setup Name | Result | Time (seconds) | Notes |
|------------|--------|----------------|-------|
| hinge_side | PASS/FAIL | | |
| routing_side | PASS/FAIL | | |

## Issues Found

[List any issues]

## Total Processing Time

[Time from click to completion]

## Log File Location

[Path to log file]
```
