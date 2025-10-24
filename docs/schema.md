# JSON Schema Documentation

## Schema Version: 1.0.0

This document describes the JSON schema used for Fusion 360 manufacturing orders.

## Root Object: Order

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `version` | string | ✅ | Schema version (format: "X.Y.Z") |
| `orderId` | string | ✅ | Unique identifier for the order |
| `timestamp` | string | ❌ | ISO 8601 timestamp (e.g., "2025-10-24T09:00:00Z") |
| `components` | array | ✅ | Array of Component objects (min: 1) |
| `outputConfig` | object | ❌ | Output file configuration |

### Example
```json
{
  "version": "1.0.0",
  "orderId": "ORDER-2025-001",
  "timestamp": "2025-10-24T09:00:00Z",
  "components": [...]
}
```

## Component Object

Each component represents one manufacturing item to be produced from a parametric Fusion model.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `componentId` | string | ✅ | Unique identifier within this order |
| `fusionModelPath` | string | ✅ | Path to .f3d file or Fusion cloud URL |
| `parameters` | object | ✅ | Parameter name-value pairs |
| `setupNames` | array | ❌ | Filter specific CAM setups (empty = all) |
| `postProcessorConfig` | object | ❌ | Post processor settings |
| `metadata` | object | ❌ | Custom metadata (free-form) |

### Example
```json
{
  "componentId": "door-panel-001",
  "fusionModelPath": "C:\\Documents\\DoorPanel.f3d",
  "parameters": {
    "component_height": "96 in",
    "component_width": "36 in",
    "door_hinging_right": 1
  }
}
```

## Parameter Values

Parameters can be specified in three formats:

### 1. String with Units (Recommended)
```json
"component_height": "96 in"
"component_width": "36.5 in"
```
**Use when**: Specifying dimensional parameters with explicit units.

### 2. Numeric Value
```json
"component_height": 96
"component_width": 36.5
```
**Use when**: The parameter unit is known and consistent. The system will append the default unit from the Fusion model.

### 3. Integer (Boolean-like)
```json
"door_hinging_right": 1
"door_swinging_out": 0
```
**Use when**: Parameter represents a boolean flag (0 = False, 1 = True).

### Complex Expressions
The system can also accept Fusion formula expressions:
```json
"custom_param": "component_height * 0.5"
```

## Post Processor Configuration

| Property | Type | Description |
|----------|------|-------------|
| `postProcessorName` | string | Name of post processor (e.g., "fanuc", "haas") |
| `outputFileName` | string | Custom output filename (without extension) |

### Example
```json
"postProcessorConfig": {
  "postProcessorName": "fanuc",
  "outputFileName": "door-panel-001"
}
```

## Output Configuration

| Property | Type | Description |
|----------|------|-------------|
| `baseDirectory` | string | Root directory for all output files |
| `includeTimestamp` | boolean | Add timestamp to output folder names |

### Example
```json
"outputConfig": {
  "baseDirectory": "C:\\Manufacturing\\Output",
  "includeTimestamp": true
}
```

## Parameter Reference

### Door Panel Parameters

These parameters are available in the door panel Fusion model:

#### Primary (User-Modifiable)
| Parameter | Unit | Valid Range | Description |
|-----------|------|-------------|-------------|
| `component_height` | in | 72-96 | Height of component |
| `component_width` | in | 22-37.5 | Width of component |
| `component_floor_clearance` | in | 1-12 | Floor clearance |
| `door_hinging_right` | - | 0 or 1 | Hinging side (relative to room) |
| `door_swinging_out` | - | 0 or 1 | Swing direction (relative to cabin) |
| `door_wall_post_hinging` | - | 0 or 1 | Wall post on hinging side |
| `door_wall_keep_latching` | - | 0 or 1 | Wall keep on latching side |

#### Derived (Auto-Computed)
These parameters are computed by Fusion based on the primary parameters:
- `component_height_limited`: Clamped height within valid range
- `component_width_limited`: Clamped width within valid range
- `component_floor_clearance_limited`: Clamped clearance
- `door_drilling_left`: Computed drilling side (0/1)
- `door_drilling_right`: Computed drilling side (0/1)
- `door_notching_left`: Computed notching requirement (0/1)
- `door_notching_right`: Computed notching requirement (0/1)
- `hole_placement`: Calculated hole position based on drilling side
- And many more...

**Important**: You should **only** specify primary parameters in your JSON. Derived parameters will be automatically recalculated by Fusion.

## Validation Rules

1. **Version must match pattern**: `\d+\.\d+\.\d+` (e.g., "1.0.0")
2. **orderId cannot be empty**
3. **Components array must have at least 1 item**
4. **Each componentId must be unique** within an order
5. **fusionModelPath must exist** (validated at runtime)
6. **Parameter names must match** Fusion model parameters (validated at runtime)
7. **Parameter values must be valid** for the parameter type

## Error Handling

The system will report errors for:
- Invalid JSON syntax
- Schema validation failures
- Missing or invalid Fusion model files
- Unknown parameter names
- Invalid parameter values or expressions
- CAM toolpath generation failures
- Post processor errors

## Best Practices

1. **Use explicit units**: `"96 in"` instead of `96`
2. **Test parameters individually**: Verify each parameter change before combining
3. **Include metadata**: Add notes for traceability
4. **Use descriptive IDs**: Make orderId and componentId human-readable
5. **Version your models**: Document which Fusion model version corresponds to each order
6. **Validate offline first**: Use schema validation tests before running in Fusion

## Example Complete Order

```json
{
  "version": "1.0.0",
  "orderId": "ORDER-2025-001",
  "timestamp": "2025-10-24T09:00:00Z",
  "components": [
    {
      "componentId": "door-panel-001",
      "fusionModelPath": "C:\\Users\\james\\Documents\\DoorPanel.f3d",
      "parameters": {
        "component_height": "96 in",
        "component_width": "36 in",
        "component_floor_clearance": "1 in",
        "door_hinging_right": 1,
        "door_swinging_out": 1,
        "door_wall_post_hinging": 0,
        "door_wall_keep_latching": 0
      },
      "setupNames": [],
      "postProcessorConfig": {
        "postProcessorName": "fanuc",
        "outputFileName": "door-panel-001"
      },
      "metadata": {
        "customerName": "Customer A",
        "orderDate": "2025-10-24",
        "notes": "Standard configuration"
      }
    }
  ],
  "outputConfig": {
    "baseDirectory": "C:\\Manufacturing\\Output",
    "includeTimestamp": true
  }
}
```

## Version History

### 1.0.0 (2025-10-24)
- Initial schema definition
- Support for parametric door panel manufacturing
- Multi-component orders
- Flexible parameter value types
- Post processor configuration
