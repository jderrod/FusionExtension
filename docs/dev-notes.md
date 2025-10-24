# Development Notes

## Technical Context

### Fusion 360 Python Environment
- **Python Version**: 3.x (embedded in Fusion 360)
- **API Modules**: `adsk.core`, `adsk.fusion`, `adsk.cam`
- **Execution Context**: Add-in runs within Fusion's event loop
- **Threading**: Main API calls must run on Fusion's main thread

### API Import Considerations
```python
import adsk.core
import adsk.fusion
import adsk.cam
```

**Common Pitfall**: The `adsk` module is only available when running inside Fusion. Unit tests for pure logic should mock these imports or isolate Fusion-dependent code.

## Development Workflow

### Phase 0: Schema & Setup ✅
**Status**: Complete

**Artifacts Created**:
- ✅ `schema.json` - JSON schema with versioning
- ✅ `samples/sample_order.json` - Example order with 2 door panels
- ✅ `README.md` - Project overview
- ✅ `docs/schema.md` - Detailed schema documentation
- ✅ `docs/dev-notes.md` - This file

**Next**: Create schema validation tests

### Phase 1: Add-in Skeleton
**Goal**: Create minimal Fusion add-in that can load and validate JSON

**Tasks**:
1. Create `src/addin.py` with:
   - `run(context)` - Entry point when add-in starts
   - `stop(context)` - Cleanup when add-in stops
   - Command registration for "Run Order"

2. Create `src/validator.py` with:
   - Schema validation using `jsonschema` library
   - JSON parsing with error handling
   - Version compatibility checking

3. Create `src/app.py` with:
   - Main application logic
   - File selection dialog
   - Validation and error reporting

**Testing Strategy**:
- Unit test `validator.py` independently (no Fusion API)
- Manual test add-in registration in Fusion
- Manual test command execution and file dialog

### Phase 2: Parameter Application
**Goal**: Apply parameter values from JSON to Fusion model

**Key Fusion API Classes**:
```python
# Access design
app = adsk.core.Application.get()
design = app.activeProduct

# Get user parameters
userParams = design.userParameters

# Find and update a parameter
param = userParams.itemByName('component_height')
param.expression = '96 in'
```

**Parameter Type Handling**:
- **String with units**: Direct assignment (`"96 in"`)
- **Numeric**: Append default unit from existing parameter
- **Integer (boolean)**: Convert to string (`"1"` or `"0"`)

**Validation**:
- Verify parameter exists before updating
- Check for errors after parameter update
- Read back parameter value to confirm

**Error Cases**:
- Unknown parameter name → Report and skip
- Invalid expression → Report and skip or fail entire component
- Circular dependencies → Fusion handles, but log warnings

### Phase 3: Toolpath Regeneration
**Goal**: Regenerate CAM toolpaths after parameter changes

**Key Fusion API Classes**:
```python
# Switch to CAM workspace
cam = adsk.cam.CAM.cast(design)

# Generate all toolpaths
future = cam.generateAllToolpaths(skipValid=True)
# skipValid=True only regenerates invalid toolpaths
# Set to False to force regenerate all
```

**Important Notes**:
- `generateAllToolpaths()` returns a `Future` object (async operation)
- Must wait for completion before post-processing
- Check `future.isGenerationCompleted` status
- Access errors via `future.errors`

**Setup Filtering**:
If `setupNames` is specified in JSON:
```python
setups = cam.setups
for setup in setups:
    if setup.name in setupNames:
        setup.generateToolpath()
```

### Phase 4: Post Processing
**Goal**: Generate G-code (.nc files) from toolpaths

**Key Fusion API Classes**:
```python
# Get CAM setup
setup = cam.setups.item(0)

# Create post input
postInput = adsk.cam.PostProcessInput.create(
    programName='output',
    postConfiguration=postConfig,
    outputFolder=outputPath,
    units=units
)

# Optional: Set specific post processor
postInput.postConfiguration = 'fanuc.cps'

# Execute post processing
setup.postProcess(postInput)
```

**Post Processor Configuration**:
- Post processors are `.cps` files (JavaScript-based)
- Located in Fusion's post library or custom folder
- Common post processors: `fanuc.cps`, `haas.cps`, `generic.cps`

**File Naming**:
- Default: Uses program name from setup
- Custom: Set via `postInput.programName`
- Our approach: Use `componentId` or `outputFileName` from JSON

**Error Handling**:
- Missing post processor → Report available processors
- Invalid toolpath → Skip and log
- Post processing errors → Capture and log

### Phase 5: Multi-Component Iteration
**Goal**: Process multiple components in sequence

**Workflow**:
```python
for component in order['components']:
    try:
        # 1. Open model (if different from current)
        open_fusion_model(component['fusionModelPath'])
        
        # 2. Apply parameters
        apply_parameters(component['parameters'])
        
        # 3. Regenerate toolpaths
        regenerate_toolpaths(component.get('setupNames', []))
        
        # 4. Post process
        post_process(component['postProcessorConfig'])
        
        # 5. Log success
        log_component_success(component['componentId'])
        
    except Exception as e:
        # Log failure but continue to next component
        log_component_failure(component['componentId'], e)
```

**Output Organization**:
```
{baseDirectory}/
  {orderId}/
    {componentId}/
      {componentId}.nc
      {componentId}_setup1.nc
      {componentId}_setup2.nc
      ...
    logs/
      {orderId}_summary.json
      {componentId}_details.log
```

## Fusion API Gotchas

### 1. Application Context
Always get the application instance:
```python
app = adsk.core.Application.get()
```
**Never** create a new Application object.

### 2. Document Management
Opening a document:
```python
doc = app.documents.open(filePath)
```
**Important**: This switches the active document. Save state if needed.

### 3. Parameter Updates Trigger Regeneration
When you update a user parameter, Fusion automatically:
- Recomputes derived parameters
- Updates features that depend on the parameter
- **Does NOT** automatically regenerate CAM toolpaths

### 4. CAM Workspace Context
Must be in CAM workspace to access CAM operations:
```python
# Check if design has CAM
if hasattr(design, 'cam'):
    cam = adsk.cam.CAM.cast(design)
else:
    # No CAM defined in this design
```

### 5. Error Handling
Fusion API errors don't always raise Python exceptions. Check return values:
```python
param = userParams.itemByName('unknown_param')
if param is None:
    # Parameter not found
```

## Testing Strategy

### Unit Tests (Pure Python)
**What to test**:
- Schema validation logic
- JSON parsing
- Parameter value formatting
- File path handling
- Error message formatting

**Mock Fusion API**:
```python
# tests/conftest.py
class MockParameter:
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

class MockUserParameters:
    def __init__(self):
        self.params = {}
    
    def itemByName(self, name):
        return self.params.get(name)
```

### Integration Tests (Manual in Fusion)
**What to test**:
1. Add-in loads without errors
2. Command appears in UI
3. File dialog opens
4. JSON validation reports errors correctly
5. Parameters update in model
6. Toolpaths regenerate
7. NC files are created with correct content

**Test Checklist**:
- [ ] Load add-in in Fusion
- [ ] Run "Run Order" command
- [ ] Select `samples/sample_order.json`
- [ ] Verify parameters updated in Parameters dialog
- [ ] Verify toolpaths regenerated in CAM workspace
- [ ] Verify .nc files created in output folder
- [ ] Verify log files contain correct information

### Regression Tests
After each phase:
1. Re-run unit tests
2. Test with sample orders
3. Verify no regressions in previous functionality

## Debugging Tips

### 1. Enable Fusion Debug Output
```python
import adsk.core
app = adsk.core.Application.get()
ui = app.userInterface
ui.messageBox('Debug message')  # Modal dialog
print('Debug output')  # Outputs to Text Commands window
```

### 2. Use Try-Except Liberally
```python
try:
    # Fusion API call
    param.expression = new_value
except Exception as e:
    ui.messageBox(f'Error: {str(e)}\n{traceback.format_exc()}')
```

### 3. Log to File
Since console output is limited:
```python
import logging
logging.basicConfig(
    filename='C:\\Temp\\fusion_addin.log',
    level=logging.DEBUG
)
```

### 4. Check API Documentation
When in doubt, check official Fusion 360 API docs (see `llms.txt`).

## Dependencies

### Required Python Packages
- `jsonschema` - JSON schema validation (may need manual installation)

### Installing Packages in Fusion Python
Fusion uses an embedded Python interpreter. To install packages:

**Option 1: Use pip in Fusion's Python**
```powershell
# Find Fusion's Python (typically in Fusion install directory)
"C:\Program Files\Autodesk\Fusion 360\Python\python.exe" -m pip install jsonschema
```

**Option 2: Copy packages manually**
Install to: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Python\Lib\site-packages\`

### Vendoring (Recommended)
To avoid installation issues, vendor the jsonschema package:
```
FusionExtension/
  src/
    vendor/
      jsonschema/  # Copy entire package here
```

## Security Considerations

1. **File Path Validation**: Ensure fusionModelPath doesn't escape expected directories
2. **JSON Size Limits**: Reject unreasonably large JSON files
3. **Parameter Injection**: Validate parameter expressions to prevent code injection
4. **Output Path Validation**: Ensure output files write to expected locations

## Performance Considerations

1. **Parameter Updates**: Batch updates when possible
2. **Toolpath Generation**: Use `skipValid=True` to avoid unnecessary regeneration
3. **File I/O**: Use buffered reading for large files
4. **Logging**: Avoid excessive debug logging in production

## Known Issues & Workarounds

### Issue: Module 'adsk' Not Found
**Cause**: Running script outside Fusion context
**Solution**: Only import `adsk` modules inside functions, not at module level

### Issue: Parameter Update Doesn't Reflect in Model
**Cause**: Parameter expression is invalid or model needs manual update
**Solution**: Call `design.updateWhenReady()` (not always available, may need to regenerate)

### Issue: Post Processor Not Found
**Cause**: Post processor name doesn't match available .cps files
**Solution**: List available post processors and validate against them

## Next Steps

1. Complete Phase 0: Add schema validation tests
2. Start Phase 1: Create add-in skeleton
3. Test add-in loading in Fusion 360
4. Implement parameter application logic

## References

See `llms.txt` for authoritative API documentation links.
