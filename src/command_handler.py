"""
Command handler for Run Order command.
Handles user interaction, file selection, and order validation.
"""

import adsk.core
import adsk.fusion
import traceback
import os
from pathlib import Path

from validator import OrderValidator
import app


class RunOrderCommandHandler(adsk.core.CommandCreatedEventHandler):
    """Handler for when the Run Order command is created"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        """
        Called when command is created.
        For Phase 1, execute immediately without showing a dialog.
        """
        try:
            app_obj = adsk.core.Application.get()
            ui = app_obj.userInterface
            
            # Get sample order file path
            repo_root = app.get_repo_root()
            sample_order = repo_root / 'samples' / 'sample_order.json'
            
            if not sample_order.exists():
                ui.messageBox(
                    f'Sample order file not found:\n{sample_order}\n\n'
                    'Please ensure samples/sample_order.json exists.',
                    'File Not Found'
                )
                return
            
            # Validate the sample file
            schema_path = str(app.get_schema_path())
            validator = OrderValidator(schema_path)
            is_valid, errors = validator.validate_json_file(str(sample_order))
            
            if not is_valid:
                error_text = 'Sample order file validation failed:\n\n' + '\n'.join(f'  • {e}' for e in errors[:5])
                if len(errors) > 5:
                    error_text += f'\n  ... and {len(errors) - 5} more errors'
                ui.messageBox(error_text, 'Validation Failed')
                return
            
            # Success! Validation complete - now process the order
            ui.messageBox(
                f'Order file validated successfully!\n\n{str(sample_order)}\n\nStarting parameter application...',
                'Processing Order',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            # Phase 2: First check what parameters exist in the current model
            current_design = app_obj.activeDocument
            if current_design:
                design = adsk.fusion.Design.cast(current_design.products.itemByProductType('DesignProductType'))
                if design:
                    from parameter_manager import ParameterManager
                    param_mgr = ParameterManager(design)
                    existing_params = param_mgr.list_all_parameters()
                    
                    if existing_params:
                        param_list = '\n'.join([f"  • {p['name']} = {p['expression']}" for p in existing_params[:15]])
                        if len(existing_params) > 15:
                            param_list += f"\n  ... and {len(existing_params) - 15} more"
                        
                        ui.messageBox(
                            f'Found {len(existing_params)} user parameters in current model:\n\n{param_list}',
                            'Current Parameters',
                            adsk.core.MessageBoxButtonTypes.OKButtonType,
                            adsk.core.MessageBoxIconTypes.InformationIconType
                        )
            
            # Phase 2: Load and process the order
            from order_processor import OrderProcessor
            
            processor = OrderProcessor(app_obj)
            success, message = processor.process_order(str(sample_order))
            
            # Show final result
            if success:
                ui.messageBox(
                    f'✓ Order Processing Complete!\n\n{message}',
                    'Success',
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.InformationIconType
                )
            else:
                ui.messageBox(
                    f'Order Processing Failed:\n\n{message}',
                    'Error',
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.WarningIconType
                )
            
        except Exception as e:
            app_obj = adsk.core.Application.get()
            ui = app_obj.userInterface
            ui.messageBox(f'Failed to execute command:\n{str(e)}\n\n{traceback.format_exc()}', 'Error')


# Phase 1: No additional handlers needed - command executes immediately
