"""
Fusion 360 Manufacturing Pipeline Add-in
Entry point file - must match the manifest name exactly.
"""

import adsk.core
import adsk.fusion
import traceback
import sys
import os

# Add src directory to path
_src_path = os.path.join(os.path.dirname(__file__), 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

# Global references
_app = None
_ui = None
_handlers = []

def run(context):
    """Called when add-in is started"""
    global _app, _ui
    
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Import after setting up path
        import app
        
        # Register the command
        app.register_command(_ui, _handlers)
        
        _ui.messageBox(
            'Fusion Manufacturing Pipeline loaded successfully.\n\n'
            'Look for "Run Order" in SOLID > CREATE dropdown.',
            'Manufacturing Pipeline'
        )
        
    except:
        if _ui:
            _ui.messageBox('Failed to initialize add-in:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Called when add-in is stopped"""
    global _ui, _handlers
    
    try:
        if _ui:
            # Import after setting up path
            import app
            
            # Unregister the command
            app.unregister_command(_ui)
            
            _ui.messageBox(
                'Fusion Manufacturing Pipeline unloaded.',
                'Manufacturing Pipeline'
            )
            
        # Clean up handlers
        _handlers.clear()
        
    except:
        if _ui:
            _ui.messageBox('Failed to clean up add-in:\n{}'.format(traceback.format_exc()))
