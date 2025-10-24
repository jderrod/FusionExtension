"""
Logging utilities for Fusion Manufacturing Pipeline.
Provides file-based logging since Fusion's console is limited.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class PipelineLogger:
    """Logger for manufacturing pipeline operations"""
    
    def __init__(self, log_dir: str = None):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory for log files (default: repo_root/logs)
        """
        if log_dir is None:
            # Default to logs directory in repo root
            repo_root = Path(__file__).parent.parent
            log_dir = repo_root / 'logs'
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('FusionManufacturingPipeline')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create file handler with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'pipeline_{timestamp}.log'
        
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler
        self.logger.addHandler(file_handler)
        
        self.log_file = log_file
        self.info(f'Logger initialized. Log file: {log_file}')
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def get_log_path(self) -> str:
        """Get path to current log file"""
        return str(self.log_file)


# Global logger instance
_global_logger = None


def get_logger() -> PipelineLogger:
    """
    Get or create global logger instance.
    
    Returns:
        PipelineLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = PipelineLogger()
    return _global_logger


def log_order_start(order_id: str, file_path: str):
    """Log start of order processing"""
    logger = get_logger()
    logger.info('=' * 80)
    logger.info(f'Starting order processing: {order_id}')
    logger.info(f'Order file: {file_path}')
    logger.info('=' * 80)


def log_order_complete(order_id: str, success: bool, message: str = ''):
    """Log completion of order processing"""
    logger = get_logger()
    logger.info('=' * 80)
    if success:
        logger.info(f'Order completed successfully: {order_id}')
    else:
        logger.error(f'Order failed: {order_id}')
    if message:
        logger.info(f'Message: {message}')
    logger.info('=' * 80)


def log_component_start(component_id: str):
    """Log start of component processing"""
    logger = get_logger()
    logger.info('-' * 80)
    logger.info(f'Processing component: {component_id}')


def log_component_complete(component_id: str, success: bool, message: str = ''):
    """Log completion of component processing"""
    logger = get_logger()
    if success:
        logger.info(f'Component completed: {component_id}')
    else:
        logger.error(f'Component failed: {component_id}')
    if message:
        logger.info(f'Message: {message}')
    logger.info('-' * 80)


def log_parameter_update(param_name: str, old_value: str, new_value: str):
    """Log parameter update"""
    logger = get_logger()
    logger.debug(f'Parameter updated: {param_name} = {new_value} (was: {old_value})')


def log_toolpath_generation(setup_name: str, success: bool, message: str = ''):
    """Log toolpath generation"""
    logger = get_logger()
    if success:
        logger.info(f'Toolpath generated: {setup_name}')
    else:
        logger.error(f'Toolpath generation failed: {setup_name}')
    if message:
        logger.debug(f'Details: {message}')


def log_post_processing(output_file: str, success: bool, message: str = ''):
    """Log post processing"""
    logger = get_logger()
    if success:
        logger.info(f'Post processing completed: {output_file}')
    else:
        logger.error(f'Post processing failed: {output_file}')
    if message:
        logger.debug(f'Details: {message}')
