"""
Main script for the Feed Downloader application.
This script orchestrates the entire data download and processing pipeline.
"""
import os
import sys
import yaml
import logging
import argparse
from typing import Dict, Any, List
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from downloader_factory import get_downloader, validate_config
from parsers.parser_factory import parse_file, detect_file_format
from utils.decompressor import decompress


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict: Configuration dictionary
    """
    logger = logging.getLogger("main")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise Exception(f"Configuration loading failed: {str(e)}")


def process_vendor(vendor_config: Dict[str, Any], global_config: Dict[str, Any]) -> bool:
    """
    Process a single vendor configuration.
    
    Args:
        vendor_config: Vendor-specific configuration
        global_config: Global configuration settings
        
    Returns:
        bool: True if processing succeeded, False otherwise
    """
    logger = logging.getLogger(f"main.{vendor_config.get('name', 'unknown')}")
    
    try:
        logger.info(f"Processing vendor: {vendor_config['name']}")
        
        # Validate vendor configuration
        if not validate_config(vendor_config):
            logger.error(f"Invalid configuration for vendor: {vendor_config['name']}")
            return False
        
        # Create downloader
        downloader = get_downloader(vendor_config)
        
        # Download data
        logger.info("Starting download...")
        local_file = downloader.download()
        logger.info(f"Download completed: {local_file}")
        
        # Handle compressed files
        files_to_process = [local_file]
        if vendor_config.get("compressed", False):
            compression_type = vendor_config.get("compression_type", "auto")
            logger.info(f"Decompressing file with type: {compression_type}")
            
            extracted_files = decompress(local_file, compression_type)
            files_to_process = extracted_files
            logger.info(f"Decompression completed: {len(extracted_files)} files extracted")
        
        # Parse and normalize data
        format_type = vendor_config.get("format")
        if format_type:
            for file_path in files_to_process:
                try:
                    logger.info(f"Parsing file: {file_path}")
                    
                    # Auto-detect format if not specified
                    if format_type == "auto":
                        format_type = detect_file_format(file_path)
                    
                    # Parse file
                    parsed_data = parse_file(file_path, format_type)
                    
                    # Save normalized data
                    if isinstance(parsed_data, dict):
                        # Multiple sheets (Excel)
                        for sheet_name, df in parsed_data.items():
                            output_path = file_path.replace(".", f"_{sheet_name}_parsed.")
                            df.to_csv(output_path, index=False)
                            logger.info(f"Saved normalized data: {output_path}")
                    else:
                        # Single DataFrame
                        output_path = file_path.replace(".", "_parsed.")
                        parsed_data.to_csv(output_path, index=False)
                        logger.info(f"Saved normalized data: {output_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to parse file {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Successfully processed vendor: {vendor_config['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process vendor {vendor_config.get('name', 'unknown')}: {str(e)}")
        return False


def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Feed Downloader - Scalable data downloader for multiple sources")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--vendor", "-v", help="Process specific vendor only")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without downloading")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger("main")
    
    try:
        logger.info("Starting Feed Downloader")
        logger.info(f"Configuration file: {args.config}")
        
        # Load configuration
        config = load_config(args.config)
        
        # Get vendors to process
        vendors = config.get("vendors", [])
        if not vendors:
            logger.error("No vendors configured")
            return 1
        
        # Filter vendors if specific vendor requested
        if args.vendor:
            vendors = [v for v in vendors if v.get("name") == args.vendor]
            if not vendors:
                logger.error(f"Vendor '{args.vendor}' not found in configuration")
                return 1
        
        # Process vendors
        successful = 0
        failed = 0
        
        for vendor_config in vendors:
            if args.dry_run:
                logger.info(f"Dry run - Validating vendor: {vendor_config['name']}")
                if validate_config(vendor_config):
                    logger.info(f"✓ Vendor '{vendor_config['name']}' configuration is valid")
                    successful += 1
                else:
                    logger.error(f"✗ Vendor '{vendor_config['name']}' configuration is invalid")
                    failed += 1
            else:
                if process_vendor(vendor_config, config):
                    successful += 1
                else:
                    failed += 1
        
        # Summary
        logger.info(f"Processing completed: {successful} successful, {failed} failed")
        
        if failed > 0:
            return 1
        else:
            return 0
            
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())