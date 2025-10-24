# Quick Start Guide

## Phase 1 Complete ✅

The Fusion 360 add-in skeleton is ready for testing in Fusion 360.

## What Was Built

**Phase 0**:
✅ Project structure, schema, validator (41 tests passing)

**Phase 1**:
✅ Fusion add-in with run/stop lifecycle  
✅ "Run Order" command in TOOLS → ADD-INS  
✅ Interactive dialog with file selection  
✅ Integrated JSON validation  
✅ Logging system (writes to logs/ directory)  

## Quick Commands

### Validate an Order
```bash
python src/validator.py samples/sample_order.json
```

### Run Tests
```bash
python -m pytest tests/test_validator.py -v
```

### Install Add-in (Windows)
```powershell
.\install_addin.ps1
```

### Install Dependencies (for development)
```bash
pip install -r requirements.txt
```

## Project Files

| File | Purpose |
|------|---------|
| `schema.json` | JSON schema definition (v1.0.0) |
| `src/validator.py` | Schema validation module |
| `tests/test_validator.py` | 41 unit tests |
| `samples/sample_order.json` | Example order with 2 door panels |
| `README.md` | Project overview |
| `docs/schema.md` | Detailed schema documentation |
| `docs/dev-notes.md` | Technical development notes |
| `PHASE0_SUMMARY.md` | Phase 0 completion report |

## Sample Order Structure

```json
{
  "version": "1.0.0",
  "orderId": "ORDER-2025-001",
  "components": [
    {
      "componentId": "door-panel-001",
      "fusionModelPath": "C:\\path\\to\\model.f3d",
      "parameters": {
        "component_height": "96 in",
        "component_width": "36 in",
        "door_hinging_right": 1
      },
      "postProcessorConfig": {
        "postProcessorName": "fanuc"
      }
    }
  ]
}
```

## Parameters Available

From `FusionModelParams/FusionModelParametersToChange.csv`:

- `component_height` - Height in inches (72-96)
- `component_width` - Width in inches (22-37.5)
- `component_floor_clearance` - Floor clearance (1-12)
- `door_hinging_right` - Hinging side (0 or 1)
- `door_swinging_out` - Swing direction (0 or 1)
- `door_wall_post_hinging` - Wall post on hinge side (0 or 1)
- `door_wall_keep_latching` - Wall keep on latch side (0 or 1)

## Test Results

```
======================== 41 passed in 0.16s ========================
```

All validation tests passing ✅

## Testing in Fusion 360

1. **Install**: Run `.\install_addin.ps1`
2. **Launch**: Open Fusion 360
3. **Load**: UTILITIES → ADD-INS → Scripts and Add-Ins → Run
4. **Execute**: TOOLS → ADD-INS → Run Order
5. **Test**: Select `samples/sample_order.json`

See `docs/PHASE1_TESTING.md` for detailed testing guide.

## Next: Phase 2

Ready to implement parameter application:
1. Load Fusion design documents
2. Read user parameters from models
3. Apply parameter values from JSON
4. Validate parameter updates
5. Log all changes

## Key Documentation

- **Schema Reference**: `docs/schema.md`
- **Development Guide**: `docs/dev-notes.md`
- **Phase 0 Report**: `PHASE0_SUMMARY.md`
- **Project Overview**: `README.md`

## Support

Refer to `llms.txt` for Fusion API documentation links.

---

**Status**: Phase 1 Complete ✅  
**Next**: Phase 2 - Parameter Application  
**Command**: "I've tested Phase 1 in Fusion. Start Phase 2 for parameter application."
