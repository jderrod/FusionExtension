"""
Unit tests for order validator

Run with: python -m pytest tests/test_validator.py -v
"""

import json
import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from validator import OrderValidator, ValidationError, validate_order_file


@pytest.fixture
def validator():
    """Create validator instance with schema"""
    return OrderValidator()


@pytest.fixture
def valid_order():
    """Return a valid order dictionary"""
    return {
        "version": "1.0.0",
        "orderId": "TEST-001",
        "timestamp": "2025-10-24T09:00:00Z",
        "components": [
            {
                "componentId": "comp-001",
                "fusionModelPath": "C:\\Models\\test.f3d",
                "parameters": {
                    "component_height": "96 in",
                    "component_width": 36.5,
                    "door_hinging_right": 1
                }
            }
        ]
    }


@pytest.fixture
def minimal_order():
    """Return minimal valid order (only required fields)"""
    return {
        "version": "1.0.0",
        "orderId": "MIN-001",
        "components": [
            {
                "componentId": "comp-001",
                "fusionModelPath": "test.f3d",
                "parameters": {}
            }
        ]
    }


class TestValidatorInit:
    """Test validator initialization"""
    
    def test_init_default_schema(self):
        """Test validator loads default schema"""
        validator = OrderValidator()
        assert validator.schema is not None
        assert 'title' in validator.schema
    
    def test_init_custom_schema(self, tmp_path):
        """Test validator with custom schema path"""
        schema_file = tmp_path / "test_schema.json"
        schema_file.write_text(json.dumps({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "TestSchema"
        }))
        
        validator = OrderValidator(str(schema_file))
        assert validator.schema['title'] == "TestSchema"
    
    def test_init_missing_schema(self):
        """Test validator fails with missing schema"""
        with pytest.raises(ValidationError, match="Schema file not found"):
            OrderValidator("/nonexistent/schema.json")


class TestBasicValidation:
    """Test basic order validation"""
    
    def test_valid_order(self, validator, valid_order):
        """Test validation passes for valid order"""
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
        assert len(errors) == 0
    
    def test_minimal_order(self, validator, minimal_order):
        """Test validation passes for minimal order"""
        is_valid, errors = validator.validate_order(minimal_order)
        assert is_valid
        assert len(errors) == 0
    
    def test_not_dict(self, validator):
        """Test validation fails for non-dict input"""
        is_valid, errors = validator.validate_order([])
        assert not is_valid
        assert "Order must be a JSON object" in errors
    
    def test_empty_order(self, validator):
        """Test validation fails for empty order"""
        is_valid, errors = validator.validate_order({})
        assert not is_valid
        assert any("version" in error for error in errors)
        assert any("orderId" in error for error in errors)
        assert any("components" in error for error in errors)


class TestVersionValidation:
    """Test version field validation"""
    
    def test_valid_version(self, validator, valid_order):
        """Test various valid version formats"""
        valid_versions = ["1.0.0", "0.0.1", "10.20.30"]
        for version in valid_versions:
            valid_order['version'] = version
            is_valid, errors = validator.validate_order(valid_order)
            assert is_valid, f"Version {version} should be valid"
    
    def test_invalid_version_format(self, validator, valid_order):
        """Test invalid version formats"""
        invalid_versions = ["1.0", "1", "v1.0.0", "1.0.0-beta", ""]
        for version in invalid_versions:
            valid_order['version'] = version
            is_valid, errors = validator.validate_order(valid_order)
            assert not is_valid
            assert any("version" in error.lower() for error in errors)
    
    def test_missing_version(self, validator, valid_order):
        """Test missing version field"""
        del valid_order['version']
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("version" in error for error in errors)


class TestOrderIdValidation:
    """Test orderId field validation"""
    
    def test_valid_order_id(self, validator, valid_order):
        """Test various valid order IDs"""
        valid_ids = ["ORDER-001", "ABC123", "test-order-2025"]
        for order_id in valid_ids:
            valid_order['orderId'] = order_id
            is_valid, errors = validator.validate_order(valid_order)
            assert is_valid
    
    def test_empty_order_id(self, validator, valid_order):
        """Test empty orderId"""
        valid_order['orderId'] = ""
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("orderId" in error for error in errors)
    
    def test_missing_order_id(self, validator, valid_order):
        """Test missing orderId"""
        del valid_order['orderId']
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("orderId" in error for error in errors)


class TestComponentsValidation:
    """Test components array validation"""
    
    def test_multiple_components(self, validator, valid_order):
        """Test order with multiple components"""
        valid_order['components'].append({
            "componentId": "comp-002",
            "fusionModelPath": "C:\\Models\\test2.f3d",
            "parameters": {"height": "80 in"}
        })
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_empty_components_array(self, validator, valid_order):
        """Test validation fails for empty components array"""
        valid_order['components'] = []
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("at least 1 item" in error for error in errors)
    
    def test_components_not_array(self, validator, valid_order):
        """Test validation fails when components is not array"""
        valid_order['components'] = {}
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("array" in error.lower() for error in errors)
    
    def test_duplicate_component_ids(self, validator, valid_order):
        """Test validation fails for duplicate componentIds"""
        valid_order['components'].append({
            "componentId": "comp-001",  # Duplicate
            "fusionModelPath": "test.f3d",
            "parameters": {}
        })
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("Duplicate componentId" in error for error in errors)


class TestComponentFieldValidation:
    """Test individual component field validation"""
    
    def test_missing_component_id(self, validator, valid_order):
        """Test component without componentId"""
        del valid_order['components'][0]['componentId']
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("componentId" in error for error in errors)
    
    def test_missing_fusion_model_path(self, validator, valid_order):
        """Test component without fusionModelPath"""
        del valid_order['components'][0]['fusionModelPath']
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("fusionModelPath" in error for error in errors)
    
    def test_missing_parameters(self, validator, valid_order):
        """Test component without parameters"""
        del valid_order['components'][0]['parameters']
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("parameters" in error for error in errors)
    
    def test_empty_component_id(self, validator, valid_order):
        """Test component with empty componentId"""
        valid_order['components'][0]['componentId'] = ""
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("componentId" in error for error in errors)
    
    def test_empty_fusion_model_path(self, validator, valid_order):
        """Test component with empty fusionModelPath"""
        valid_order['components'][0]['fusionModelPath'] = ""
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("fusionModelPath" in error for error in errors)


class TestParameterValidation:
    """Test parameter validation"""
    
    def test_string_parameters(self, validator, valid_order):
        """Test string parameter values"""
        valid_order['components'][0]['parameters'] = {
            "height": "96 in",
            "width": "36.5 in",
            "expression": "height * 2"
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_numeric_parameters(self, validator, valid_order):
        """Test numeric parameter values"""
        valid_order['components'][0]['parameters'] = {
            "height": 96.0,
            "width": 36.5,
            "count": 5
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_integer_parameters(self, validator, valid_order):
        """Test integer parameter values (for booleans)"""
        valid_order['components'][0]['parameters'] = {
            "door_hinging_right": 1,
            "door_swinging_out": 0
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_parameters_not_dict(self, validator, valid_order):
        """Test validation fails when parameters is not dict"""
        valid_order['components'][0]['parameters'] = []
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("parameters must be an object" in error for error in errors)
    
    def test_invalid_parameter_type(self, validator, valid_order):
        """Test validation fails for invalid parameter types"""
        valid_order['components'][0]['parameters'] = {
            "invalid": None  # None is not allowed
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("Invalid value type" in error for error in errors)


class TestOptionalFields:
    """Test optional field validation"""
    
    def test_timestamp_present(self, validator, valid_order):
        """Test with timestamp field"""
        # Already present in valid_order fixture
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_timestamp_absent(self, validator, valid_order):
        """Test without timestamp field"""
        del valid_order['timestamp']
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_setup_names_present(self, validator, valid_order):
        """Test with setupNames field"""
        valid_order['components'][0]['setupNames'] = ["Setup1", "Setup2"]
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_setup_names_empty(self, validator, valid_order):
        """Test with empty setupNames array"""
        valid_order['components'][0]['setupNames'] = []
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_setup_names_invalid(self, validator, valid_order):
        """Test with invalid setupNames"""
        valid_order['components'][0]['setupNames'] = [1, 2, 3]
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("setupNames" in error for error in errors)
    
    def test_post_processor_config(self, validator, valid_order):
        """Test with postProcessorConfig"""
        valid_order['components'][0]['postProcessorConfig'] = {
            "postProcessorName": "fanuc",
            "outputFileName": "output"
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_metadata_present(self, validator, valid_order):
        """Test with metadata field"""
        valid_order['components'][0]['metadata'] = {
            "customer": "Test Customer",
            "notes": "Test notes",
            "customField": 123
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid


class TestOutputConfig:
    """Test output configuration validation"""
    
    def test_output_config_valid(self, validator, valid_order):
        """Test with valid output config"""
        valid_order['outputConfig'] = {
            "baseDirectory": "C:\\Output",
            "includeTimestamp": True
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_output_config_partial(self, validator, valid_order):
        """Test with partial output config"""
        valid_order['outputConfig'] = {
            "baseDirectory": "C:\\Output"
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert is_valid
    
    def test_output_config_invalid_type(self, validator, valid_order):
        """Test with invalid includeTimestamp type"""
        valid_order['outputConfig'] = {
            "includeTimestamp": "true"  # Should be boolean
        }
        is_valid, errors = validator.validate_order(valid_order)
        assert not is_valid
        assert any("includeTimestamp" in error for error in errors)


class TestFileValidation:
    """Test file-based validation"""
    
    def test_validate_sample_file(self, validator):
        """Test validation of sample order file"""
        sample_path = Path(__file__).parent.parent / "samples" / "sample_order.json"
        if sample_path.exists():
            is_valid, errors = validator.validate_json_file(str(sample_path))
            assert is_valid, f"Sample file should be valid. Errors: {errors}"
    
    def test_validate_nonexistent_file(self, validator):
        """Test validation of non-existent file"""
        is_valid, errors = validator.validate_json_file("/nonexistent/file.json")
        assert not is_valid
        assert any("not found" in error for error in errors)
    
    def test_validate_invalid_json_syntax(self, validator, tmp_path):
        """Test validation of file with invalid JSON syntax"""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json")
        
        is_valid, errors = validator.validate_json_file(str(bad_file))
        assert not is_valid
        assert any("Invalid JSON" in error for error in errors)


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_validate_order_file_function(self):
        """Test standalone validate_order_file function"""
        sample_path = Path(__file__).parent.parent / "samples" / "sample_order.json"
        if sample_path.exists():
            is_valid, errors = validate_order_file(str(sample_path))
            assert is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
