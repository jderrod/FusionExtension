"""
Main application logic for Fusion Manufacturing Pipeline.
Handles command registration and coordination.
"""

import adsk.core
import adsk.fusion
import traceback
import os
from pathlib import Path

from command_handler import RunOrderCommandHandler

# Command identifiers
COMMAND_ID = 'ManufacturingPipelineRunOrder'
COMMAND_NAME = 'Run Order'
COMMAND_DESCRIPTION = 'Process a manufacturing order from JSON file'
COMMAND_TOOLTIP = 'Load and process a JSON manufacturing order'

# UI location
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'  # The SOLID panel in DESIGN tab


def register_command(ui: adsk.core.UserInterface, handlers: list):
    """
    Register the Run Order command in Fusion UI.
    
    Args:
        ui: Fusion UserInterface object
        handlers: List to store command handlers (prevents garbage collection)
    """
    try:
        # Get the target workspace and panel
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if not workspace:
            ui.messageBox(f'Workspace not found: {WORKSPACE_ID}')
            return
        
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if not panel:
            ui.messageBox(f'Panel not found: {PANEL_ID}')
            return
        
        # Check if command already exists (cleanup from previous run)
        cmd_def = ui.commandDefinitions.itemById(COMMAND_ID)
        if cmd_def:
            cmd_def.deleteMe()
        
        # Create command definition
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID,
            COMMAND_NAME,
            COMMAND_DESCRIPTION,
            ''  # No custom icon for now
        )
        
        # Tooltip is already set in the description parameter above
        # toolClipFilename is for an image file, not text
        
        # Create and connect command handler
        handler = RunOrderCommandHandler()
        cmd_def.commandCreated.add(handler)
        handlers.append(handler)
        
        # Find the CREATE dropdown in the SOLID panel (PCB Create dropdown)
        create_dropdown = None
        for ctrl in panel.controls:
            if ctrl.objectType == adsk.core.DropDownControl.classType():
                dropdown_ctrl = adsk.core.DropDownControl.cast(ctrl)
                # Look for any dropdown with 'create' in the name
                if 'create' in dropdown_ctrl.id.lower():
                    create_dropdown = dropdown_ctrl
                    break
        
        if create_dropdown:
            # Add to CREATE dropdown
            control = create_dropdown.controls.itemById(COMMAND_ID)
            if not control:
                create_dropdown.controls.addCommand(cmd_def)
        else:
            # Fallback: add directly to panel
            control = panel.controls.itemById(COMMAND_ID)
            if not control:
                panel.controls.addCommand(cmd_def)
        
    except:
        ui.messageBox(f'Failed to register command:\n{traceback.format_exc()}')


def unregister_command(ui: adsk.core.UserInterface):
    """
    Unregister the Run Order command from Fusion UI.
    
    Args:
        ui: Fusion UserInterface object
    """
    try:
        # Get the target workspace and panel
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if workspace:
            panel = workspace.toolbarPanels.itemById(PANEL_ID)
            if panel:
                # Remove control from panel
                control = panel.controls.itemById(COMMAND_ID)
                if control:
                    control.deleteMe()
        
        # Remove command definition
        cmd_def = ui.commandDefinitions.itemById(COMMAND_ID)
        if cmd_def:
            cmd_def.deleteMe()
            
    except:
        ui.messageBox(f'Failed to unregister command:\n{traceback.format_exc()}')


def get_repo_root() -> Path:
    """
    Get the repository root directory.
    
    Returns:
        Path object pointing to repo root
    """
    # Go up from src/ to repo root
    return Path(__file__).parent.parent


def get_schema_path() -> Path:
    """
    Get path to schema.json.
    
    Returns:
        Path object pointing to schema.json
    """
    return get_repo_root() / 'schema.json'


def get_log_directory() -> Path:
    """
    Get or create log directory.
    
    Returns:
        Path object pointing to logs directory
    """
    log_dir = get_repo_root() / 'logs'
    log_dir.mkdir(exist_ok=True)
    return log_dir
