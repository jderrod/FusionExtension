"""
Order Processor for Fusion 360 Manufacturing Pipeline
Handles loading orders, opening documents, and coordinating operations
"""

import adsk.core
import adsk.fusion
import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from parameter_manager import ParameterManager
from cam_manager import CAMManager
from post_processor import PostProcessor
from logger import get_logger


class OrderProcessor:
    """Processes manufacturing orders from JSON files"""
    
    def __init__(self, app: adsk.core.Application):
        """
        Initialize order processor.
        
        Args:
            app: Fusion Application object
        """
        self.app = app
        self.ui = app.userInterface
        self.logger = get_logger()
    
    def load_order_file(self, file_path: str) -> Optional[Dict]:
        """
        Load and parse order JSON file.
        
        Args:
            file_path: Path to JSON order file
            
        Returns:
            Parsed order dictionary or None on error
        """
        try:
            with open(file_path, 'r') as f:
                order = json.load(f)
            return order
        except Exception as e:
            self.ui.messageBox(f'Failed to load order file:\n{str(e)}', 'Error')
            return None
    
    def open_document(self, file_path: str) -> Tuple[bool, Optional[adsk.core.Document]]:
        """
        Open a Fusion 360 document. If a document with matching name is already open, uses that.
        
        Args:
            file_path: Path to .f3d or cloud document, or just filename
            
        Returns:
            Tuple of (success: bool, document: Document or None)
        """
        try:
            # Extract just the filename from path
            file_name = os.path.basename(file_path)
            
            # Check if a document with this name is already open
            self.logger.info(f'Looking for open document: {file_name}')
            for doc in self.app.documents:
                if doc.name == file_name or doc.name == file_name.replace('.f3d', ''):
                    self.logger.info(f'Found already open document: {doc.name}')
                    self.ui.messageBox(
                        f'Using currently open document:\n{doc.name}',
                        'Document Found',
                        adsk.core.MessageBoxButtonTypes.OKButtonType,
                        adsk.core.MessageBoxIconTypes.InformationIconType
                    )
                    return True, doc
            
            # Document not open, try to open it
            self.logger.info(f'Document not open, attempting to open: {file_path}')
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.logger.error(f'File not found: {file_path}')
                return False, None
            
            # Open the document
            doc = self.app.documents.open(file_path)
            
            if not doc:
                return False, None
            
            self.logger.info(f'Successfully opened document: {doc.name}')
            return True, doc
            
        except Exception as e:
            self.logger.exception('Failed to open document')
            self.ui.messageBox(f'Failed to open document:\n{file_path}\n\n{str(e)}', 'Error')
            return False, None
    
    def process_order(self, order_file_path: str) -> Tuple[bool, str]:
        """
        Process a complete manufacturing order.
        
        Args:
            order_file_path: Path to order JSON file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load order
            self.logger.info(f'Loading order from: {order_file_path}')
            order = self.load_order_file(order_file_path)
            if not order:
                self.logger.error('Failed to load order file')
                return False, 'Failed to load order file'
            
            order_id = order.get('orderId', 'unknown')
            components = order.get('components', [])
            
            self.logger.info(f'Processing order: {order_id} with {len(components)} component(s)')
            
            if not components:
                return False, 'No components found in order'
            
            results = []
            
            # Process each component
            for idx, component in enumerate(components):
                comp_result = self.process_component(component, idx + 1, len(components))
                results.append(comp_result)
            
            # Summary
            success_count = sum(1 for r in results if r[0])
            total_count = len(results)
            
            if success_count == total_count:
                message = f'Order {order_id} completed successfully!\n\n'
                message += f'Processed {total_count} component(s)'
                return True, message
            else:
                message = f'Order {order_id} partially completed.\n\n'
                message += f'{success_count}/{total_count} components successful\n\n'
                message += 'Failed components:\n'
                for i, (success, msg) in enumerate(results):
                    if not success:
                        message += f'  Component {i+1}: {msg}\n'
                return False, message
            
        except Exception as e:
            return False, f'Order processing failed: {str(e)}'
    
    def process_component(self, component: Dict, comp_num: int, total_comps: int) -> Tuple[bool, str]:
        """
        Process a single component from the order.
        
        Args:
            component: Component dictionary from order
            comp_num: Component number (1-indexed)
            total_comps: Total number of components
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            comp_id = component.get('componentId', f'Component{comp_num}')
            fusion_file = component.get('fusionModelPath', '')
            parameters = component.get('parameters', {})
            
            self.logger.info(f'Processing component {comp_num}/{total_comps}: {comp_id}')
            self.logger.info(f'  Fusion file: {fusion_file}')
            self.logger.info(f'  Parameters to apply: {len(parameters)}')
            
            # Validate component data
            if not fusion_file:
                return False, f'{comp_id}: No fusionFile specified'
            
            if not parameters:
                return False, f'{comp_id}: No parameters specified'
            
            # Show progress
            self.ui.messageBox(
                f'Processing component {comp_num} of {total_comps}:\n{comp_id}',
                'Processing',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            # Open the document
            success, doc = self.open_document(fusion_file)
            if not success:
                return False, f'{comp_id}: Failed to open document: {fusion_file}'
            
            # Get the design
            design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            if not design:
                return False, f'{comp_id}: No design found in document'
            
            # Apply parameters
            self.logger.info(f'Applying parameters to {comp_id}')
            param_mgr = ParameterManager(design)
            results = param_mgr.update_parameters_batch(parameters)
            
            # Log each parameter update
            for param_name, success, msg in results:
                if success:
                    self.logger.info(f'  ✓ {msg}')
                else:
                    self.logger.error(f'  ✗ {msg}')
            
            # Check results
            failed_params = [r for r in results if not r[1]]
            if failed_params:
                error_msg = f'{comp_id}: Some parameters failed to update:\n'
                for param_name, success, msg in failed_params:
                    error_msg += f'  {msg}\n'
                return False, error_msg
            
            # Success! Parameters updated
            success_msg = f'{comp_id}: Successfully updated {len(parameters)} parameter(s)'
            
            # Show detailed results
            details = '\n'.join([f'  {msg}' for _, _, msg in results])
            self.ui.messageBox(
                f'{success_msg}\n\n{details}',
                'Parameters Updated',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            self.logger.info(f'{comp_id}: Parameter updates complete, starting CAM regeneration')
            
            # Phase 3: Regenerate CAM toolpaths
            cam_mgr = CAMManager(self.app, doc)
            
            # Get CAM product (no need to activate workspace)
            self.logger.info(f'{comp_id}: Accessing CAM product')
            cam_success, cam_msg = cam_mgr.get_cam_product()
            
            if not cam_success:
                self.logger.error(f'{comp_id}: {cam_msg}')
                return False, f'{comp_id}: CAM access failed: {cam_msg}'
            
            self.logger.info(f'{comp_id}: {cam_msg}')
            
            # List available setups
            setup_names = cam_mgr.list_setup_names()
            self.logger.info(f'{comp_id}: Found {len(setup_names)} CAM setup(s): {", ".join(setup_names)}')
            
            if not setup_names:
                return False, f'{comp_id}: No CAM setups found in document'
            
            # Show setups found
            self.ui.messageBox(
                f'Found {len(setup_names)} CAM setup(s):\n  • ' + '\n  • '.join(setup_names) + '\n\nRegenerating toolpaths...',
                'CAM Setups Found',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            # Regenerate ALL toolpaths (requirement: always regenerate all setups)
            self.logger.info(f'{comp_id}: Regenerating toolpaths for all setups')
            regen_success, regen_msg, regen_results = cam_mgr.regenerate_all_toolpaths()
            
            # Log results
            for setup_name, success, msg in regen_results:
                if success:
                    self.logger.info(f'{comp_id}: Setup "{setup_name}": {msg}')
                else:
                    self.logger.error(f'{comp_id}: Setup "{setup_name}": {msg}')
            
            # If regeneration failed, fail entire order (requirement)
            if not regen_success:
                self.logger.error(f'{comp_id}: Toolpath regeneration failed: {regen_msg}')
                
                # Show error details
                error_details = '\n'.join([f'  • {name}: {msg}' for name, success, msg in regen_results if not success])
                self.ui.messageBox(
                    f'{comp_id}: Toolpath regeneration FAILED!\n\n{regen_msg}\n\n{error_details}',
                    'Toolpath Generation Failed',
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.CriticalIconType
                )
                
                return False, f'{comp_id}: Toolpath regeneration failed: {regen_msg}'
            
            # Phase 4: Post process all setups to generate G-code
            self.logger.info(f'{comp_id}: Starting post processing')
            
            # Get output directory - hardcoded for now, could be from JSON later
            output_dir = r'C:\Users\james.derrod\OneDrive - Bobrick Washroom Equipment\Documents\Fusion 360\NC Programs'
            
            post_proc = PostProcessor(self.app, output_dir)
            
            # Get all setups for post processing
            all_setups = cam_mgr.get_all_setups()
            
            # Show starting message
            self.ui.messageBox(
                f'Toolpaths regenerated successfully!\n\nStarting post processing for {len(all_setups)} setup(s)...',
                'Post Processing',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            # Post process all setups
            post_success, post_msg, post_results = post_proc.post_process_all_setups(cam_mgr.cam_product, all_setups)
            
            # Log post processing results
            for setup_name, success, msg, file_path in post_results:
                if success:
                    self.logger.info(f'{comp_id}: Post "{setup_name}": {msg}')
                else:
                    self.logger.error(f'{comp_id}: Post "{setup_name}": {msg}')
            
            # Check if at least some setups posted successfully
            successful_posts = [r for r in post_results if r[1]]
            
            if not successful_posts:
                # All post processing failed - this is an error
                self.logger.error(f'{comp_id}: All post processing failed')
                
                error_details = '\n'.join([f'  • {name}: {msg}' for name, success, msg, _ in post_results if not success])
                self.ui.messageBox(
                    f'{comp_id}: Post processing FAILED!\n\n{post_msg}\n\n{error_details}',
                    'Post Processing Failed',
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.CriticalIconType
                )
                
                return False, f'{comp_id}: Post processing failed: {post_msg}'
            
            # Success! Show final results
            self.logger.info(f'{comp_id}: All operations complete')
            
            final_msg = f'{comp_id}: Processing complete!\n\n'
            final_msg += f'✓ Updated {len(parameters)} parameter(s)\n'
            final_msg += f'✓ Regenerated {len(setup_names)} CAM setup(s)\n'
            final_msg += f'✓ Generated {len(successful_posts)}/{len(all_setups)} NC program(s):\n'
            
            for setup_name, success, msg, file_path in post_results:
                if success:
                    # Extract just filename from path
                    filename = os.path.basename(file_path) if file_path else 'unknown'
                    final_msg += f'    • {setup_name}: {filename}\n'
                else:
                    final_msg += f'    • {setup_name}: FAILED ({msg})\n'
            
            final_msg += f'\nOutput: {output_dir}'
            
            self.ui.messageBox(
                final_msg,
                'Component Complete',
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )
            
            return True, f'{comp_id}: Complete - {len(successful_posts)} NC file(s) generated'
            
        except Exception as e:
            return False, f'{comp_id}: Exception: {str(e)}'
    
    def get_current_design(self) -> Optional[adsk.fusion.Design]:
        """
        Get the currently active design.
        
        Returns:
            Design object or None
        """
        try:
            doc = self.app.activeDocument
            if not doc:
                return None
            
            design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            return design
            
        except:
            return None
