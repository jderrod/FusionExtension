"""
Parameter Manager for Fusion 360 Manufacturing Pipeline
Handles reading and updating user parameters in Fusion models
"""

import adsk.core
import adsk.fusion
from typing import Dict, List, Tuple, Optional


class ParameterManager:
    """Manages parameter operations for Fusion 360 designs"""
    
    def __init__(self, design: adsk.fusion.Design):
        """
        Initialize parameter manager.
        
        Args:
            design: Fusion Design object
        """
        self.design = design
        self.user_parameters = design.userParameters
    
    def get_all_parameters(self) -> Dict[str, str]:
        """
        Get all user parameters and their current values.
        
        Returns:
            Dictionary mapping parameter name to expression (value with units)
        """
        params = {}
        for param in self.user_parameters:
            params[param.name] = param.expression
        return params
    
    def get_parameter_value(self, param_name: str) -> Optional[str]:
        """
        Get a specific parameter's current value.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            Parameter expression (value with units) or None if not found
        """
        param = self.user_parameters.itemByName(param_name)
        if param:
            return param.expression
        return None
    
    def update_parameter(self, param_name: str, new_value: str) -> Tuple[bool, str]:
        """
        Update a parameter's value.
        
        Args:
            param_name: Name of the parameter to update
            new_value: New value as string (can include units, e.g., "100 mm", "2.5", "45 deg")
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get the parameter
            param = self.user_parameters.itemByName(param_name)
            
            if not param:
                return False, f"Parameter '{param_name}' not found in model"
            
            # Store old value for logging
            old_value = param.expression
            
            # Update the parameter expression
            param.expression = new_value
            
            return True, f"Updated '{param_name}' from '{old_value}' to '{new_value}'"
            
        except Exception as e:
            return False, f"Failed to update '{param_name}': {str(e)}"
    
    def update_parameters_batch(self, parameters: Dict[str, str]) -> List[Tuple[str, bool, str]]:
        """
        Update multiple parameters at once.
        
        Args:
            parameters: Dictionary mapping parameter name to new value
            
        Returns:
            List of tuples (param_name, success, message) for each parameter
        """
        results = []
        
        for param_name, new_value in parameters.items():
            success, message = self.update_parameter(param_name, new_value)
            results.append((param_name, success, message))
        
        return results
    
    def validate_parameters_exist(self, param_names: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if all specified parameters exist in the model.
        
        Args:
            param_names: List of parameter names to check
            
        Returns:
            Tuple of (all_exist: bool, missing_params: List[str])
        """
        missing = []
        
        for param_name in param_names:
            param = self.user_parameters.itemByName(param_name)
            if not param:
                missing.append(param_name)
        
        return len(missing) == 0, missing
    
    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, any]]:
        """
        Get detailed information about a parameter.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            Dictionary with parameter details or None if not found
        """
        param = self.user_parameters.itemByName(param_name)
        
        if not param:
            return None
        
        return {
            'name': param.name,
            'expression': param.expression,
            'value': param.value,
            'unit': param.unit,
            'comment': param.comment if hasattr(param, 'comment') else '',
            'is_favorite': param.isFavorite if hasattr(param, 'isFavorite') else False
        }
    
    def list_all_parameters(self) -> List[Dict[str, any]]:
        """
        Get detailed information about all user parameters.
        
        Returns:
            List of parameter info dictionaries
        """
        params = []
        for param in self.user_parameters:
            params.append({
                'name': param.name,
                'expression': param.expression,
                'value': param.value,
                'unit': param.unit
            })
        return params


def format_parameter_value(value: any, param_type: str = "string") -> str:
    """
    Format a parameter value for Fusion 360 parameter expression.
    
    Args:
        value: Raw value (string, number, etc.)
        param_type: Type hint - "string" (with units), "numeric", or "integer"
        
    Returns:
        Formatted expression string
    """
    if param_type == "string":
        # Assume it already has units like "100 mm" or "45 deg"
        return str(value)
    elif param_type == "numeric":
        # Pure number
        return str(float(value))
    elif param_type == "integer":
        # Integer value
        return str(int(value))
    else:
        # Default: return as-is
        return str(value)
