# Phase 4 Summary: Post Processing & G-code Generation

**Status**: READY FOR TESTING  
**Date**: October 24, 2025  

## Objectives

✅ Generate G-code files from CAM toolpaths  
✅ Support RichAuto DSP post processor (richauto.cps)  
✅ Auto-incrementing program numbers (1001, 1002, 1003, ...)  
✅ One NC file per setup  
✅ Persistent counter across runs  
✅ Handle setup failures gracefully (routing_side may fail)

## Implementation

### New Module Created

**src/post_processor.py** (210 lines)
- `PostProcessor` class for G-code generation
- Auto-incrementing program counter with persistence
- One file per setup generation
- RichAuto DSP post processor integration
- Error handling and validation

### Integration

- Updated `src/order_processor.py` to call post processing after toolpath regeneration
- Hardcoded output directory: `C:\Users\james.derrod\OneDrive - Bobrick Washroom Equipment\Documents\Fusion 360\NC Programs`
- Program counter stored in: `nc_program_counter.txt` (project root)

## Key Features

### Auto-Incrementing Program Numbers
- Starts at **1001** on first run
- Increments for each setup: 1001, 1002, 1003, ...
- Counter persists across runs via `nc_program_counter.txt`
- Counter survives add-in restarts and Fusion restarts

### Output File Naming
- Format: `{program_number}.nc`
- Example: `1001.nc`, `1002.nc`
- One file per setup

### Post Processor
- **Name**: richauto (RichAuto DSP)
- **File**: richauto.cps (from Fusion's post processor library)
- **Location**: Fusion's generic post folder
- **Units**: Uses document units

### Error Handling
- Checks if setup has valid toolpaths before posting
- Verifies post processor exists
- Validates output files were created
- Allows partial success (some setups fail, others succeed)
- **routing_side setup expected to fail** - that's okay!

## Workflow

```
1. Parameters updated (Phase 2)
   ↓
2. Toolpaths regenerated (Phase 3)
   ↓
3. For each setup:
   - Get next program number
   - Post process setup
   - Generate {number}.nc file
   ↓
4. Show results:
   - hinge_side: 1001.nc ✓
   - routing_side: FAILED (expected)
   ↓
5. Order complete!
```

## Expected Output

### Success Case
```
Door Panel: Processing complete!

✓ Updated 7 parameter(s)
✓ Regenerated 2 CAM setup(s)
✓ Generated 1/2 NC program(s):
    • hinge_side: 1001.nc
    • routing_side: FAILED (Setup has no valid toolpaths)

Output: C:\Users\james.derrod\OneDrive - Bobrick Washroom Equipment\Documents\Fusion 360\NC Programs
```

### Output Files
- `1001.nc` - G-code for hinge_side setup
- (routing_side doesn't generate due to pre-existing errors)

### Next Run
- `1002.nc` - Next hinge_side
- Counter automatically increments

## Program Counter File

**Location**: `c:\Users\james.derrod\FusionExtension\nc_program_counter.txt`

**Format**: Single integer
```
1001
```

**Behavior**:
- Created on first run with value: 1001
- Incremented for each setup processed
- Persists across add-in restarts
- Persists across Fusion 360 restarts

**Reset Counter**:
To reset back to 1001, simply delete the file or edit its content.

## Configuration

### Hardcoded Settings
```python
# Output directory
output_dir = r'C:\Users\james.derrod\OneDrive - Bobrick Washroom Equipment\Documents\Fusion 360\NC Programs'

# Post processor
post_config = cam.genericPostFolder + '/richauto.cps'

# File extension
.nc

# Starting program number
1001
```

### Future: JSON Configuration (Phase 5+)
Could be moved to JSON order file:
```json
"outputConfig": {
  "baseDirectory": "C:\\Output",
  "postProcessor": "richauto",
  "startingProgramNumber": 1001
}
```

## Testing Procedure

### Test 1: First Run

**Expected**:
1. Counter file created with 1001
2. hinge_side → `1001.nc` generated
3. routing_side → Fails (no valid toolpaths)
4. Order succeeds with 1/2 files

### Test 2: Second Run

**Expected**:
1. Counter reads 1001, increments
2. hinge_side → `1002.nc` generated
3. routing_side → Fails again
4. Order succeeds with 1/2 files

### Test 3: Verify Counter

```powershell
Get-Content C:\Users\james.derrod\FusionExtension\nc_program_counter.txt
# Should show: 1002
```

### Test 4: Verify Output Files

```powershell
Get-ChildItem "C:\Users\james.derrod\OneDrive - Bobrick Washroom Equipment\Documents\Fusion 360\NC Programs" -Filter *.nc | Sort-Object LastWriteTime -Descending
```

**Expected**: `1001.nc`, `1002.nc`, etc.

### Test 5: Inspect G-code

Open `1001.nc` in text editor:
- Should contain RichAuto DSP formatted code
- Check program number references
- Verify tool changes, feed rates, etc.

## Success Criteria

✅ Program counter starts at 1001  
✅ Counter increments for each setup  
✅ Counter persists across runs  
✅ hinge_side generates NC file successfully  
✅ routing_side fails gracefully (expected)  
✅ Order completes successfully  
✅ Output files created in correct directory  
✅ G-code is valid RichAuto format

## Troubleshooting

### Issue: "Post processor not found"

**Cause**: richauto.cps not in Fusion's post library

**Solutions**:
1. Check Fusion's post processor library location
2. In MANUFACTURE workspace → Post Process → verify "richauto" exists
3. May need to download from Autodesk or specify full path

### Issue: No output files generated

**Cause**: Output directory doesn't exist or no write permissions

**Solutions**:
1. Verify directory exists: `C:\Users\james.derrod\OneDrive...\NC Programs`
2. Check write permissions
3. Try running Fusion as administrator

### Issue: Counter keeps resetting to 1001

**Cause**: Counter file not persisting

**Solutions**:
1. Check if `nc_program_counter.txt` exists in project root
2. Verify write permissions
3. Check if file is being deleted between runs

### Issue: "Setup has no valid toolpaths"

**Cause**: Setup's operations all have errors (expected for routing_side)

**Solution**: This is expected! Fix the CAM operations in MANUFACTURE workspace if you want that setup to post.

## Logs

Check detailed logs at:
```powershell
Get-Content (Get-ChildItem C:\Users\james.derrod\FusionExtension\logs\pipeline_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 50
```

**Expected log entries**:
```
INFO - Starting post processing
INFO - Post "hinge_side": Generated 1001.nc (15234 bytes)
ERROR - Post "routing_side": Setup 'routing_side' has no valid toolpaths to post
INFO - All operations complete
```

## Known Limitations

1. **Output directory hardcoded** - Not configurable per order yet
2. **No program name customization** - Always uses program number
3. **No combined output** - Each setup is separate file
4. **routing_side always fails** - Pre-existing CAM errors need fixing

## Next Phase: Phase 5 (Optional)

Phase 5 would add:
- Multi-component batch processing
- Process multiple orders in sequence
- JSON-configurable output directory
- Error recovery and retry logic

## Files Modified

### New Files
- `src/post_processor.py`
- `nc_program_counter.txt` (auto-created on first run)
- `PHASE4_SUMMARY.md`

### Updated Files
- `src/order_processor.py` - Integrated post processing

### Generated Files
- `{program_number}.nc` - G-code output files in NC Programs folder
- `logs/pipeline_*.log` - Execution logs

## Complete Workflow (All Phases)

```
Phase 1: Add-in loads, command registered
   ↓
Phase 2: Load order JSON → Update parameters
   ↓
Phase 3: Regenerate toolpaths for all setups
   ↓
Phase 4: Post process each setup → Generate NC files
   ↓
Result: Ready for manufacturing!
```

## Phase 4 Status: READY FOR TESTING ✅

**Next Steps**:
1. Restart add-in
2. Run order: SOLID → CREATE (PCB) → Run Order
3. Check for NC files in output directory
4. Verify program counter incremented
5. Inspect G-code content

Ready to test! 🚀
