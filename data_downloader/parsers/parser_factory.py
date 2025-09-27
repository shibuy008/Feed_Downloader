"""
Factory for creating parser instances based on file format.
"""
import pandas as pd
import logging
from typing import Dict, Any, Union, List
from .csv_parser import parse_csv, parse_csv_with_schema
from .json_parser import parse_json, parse_json_with_path, parse_json_stream
from .xml_parser import parse_xml, parse_xml_with_xpath, parse_xml_rss
from .excel_parser import parse_excel, parse_excel_sheet, parse_excel_with_schema


def parse_file(file_path: str, file_format: str, **kwargs) -> Union[pd.DataFrame, Dict[str, pd.DataFrame], List[pd.DataFrame]]:
    """
    Parse file based on format type.
    
    Args:
        file_path: Path to the file to parse
        file_format: Format of the file (csv, json, xml, excel, etc.)
        **kwargs: Additional arguments to pass to the parser
        
    Returns:
        pd.DataFrame, Dict[str, pd.DataFrame], or List[pd.DataFrame]: Parsed data
        
    Raises:
        ValueError: If the format is not supported
        Exception: If parsing fails
    """
    logger = logging.getLogger("parser.factory")
    
    try:
        format_lower = file_format.lower()
        
        if format_lower == "csv":
            return parse_csv(file_path, **kwargs)
        elif format_lower == "json":
            return parse_json(file_path, **kwargs)
        elif format_lower == "xml":
            return parse_xml(file_path, **kwargs)
        elif format_lower in ["xls", "xlsx", "excel"]:
            return parse_excel(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
            
    except Exception as e:
        logger.error(f"Failed to parse file {file_path} with format {file_format}: {str(e)}")
        raise Exception(f"File parsing failed: {str(e)}")


def parse_file_with_schema(file_path: str, file_format: str, schema: Dict[str, Any]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Parse file with a predefined schema.
    
    Args:
        file_path: Path to the file to parse
        file_format: Format of the file
        schema: Schema configuration for parsing
        
    Returns:
        pd.DataFrame or Dict[str, pd.DataFrame]: Parsed data with applied schema
    """
    logger = logging.getLogger("parser.factory")
    
    try:
        format_lower = file_format.lower()
        
        if format_lower == "csv":
            return parse_csv_with_schema(file_path, schema)
        elif format_lower in ["xls", "xlsx", "excel"]:
            return parse_excel_with_schema(file_path, schema)
        else:
            # For other formats, use regular parsing
            return parse_file(file_path, file_format)
            
    except Exception as e:
        logger.error(f"Failed to parse file with schema {file_path}: {str(e)}")
        raise Exception(f"File parsing with schema failed: {str(e)}")


def parse_file_advanced(file_path: str, file_format: str, parsing_options: Dict[str, Any]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame], List[pd.DataFrame]]:
    """
    Parse file with advanced options.
    
    Args:
        file_path: Path to the file to parse
        file_format: Format of the file
        parsing_options: Advanced parsing options
        
    Returns:
        Parsed data based on options
    """
    logger = logging.getLogger("parser.factory")
    
    try:
        format_lower = file_format.lower()
        
        if format_lower == "json":
            # Handle JSON-specific options
            if "json_path" in parsing_options:
                return parse_json_with_path(file_path, parsing_options["json_path"])
            elif parsing_options.get("stream", False):
                return parse_json_stream(file_path)
            else:
                return parse_json(file_path, **parsing_options)
                
        elif format_lower == "xml":
            # Handle XML-specific options
            if "xpath" in parsing_options:
                return parse_xml_with_xpath(file_path, parsing_options["xpath"])
            elif parsing_options.get("rss", False):
                return parse_xml_rss(file_path)
            else:
                return parse_xml(file_path, **parsing_options)
                
        elif format_lower in ["xls", "xlsx", "excel"]:
            # Handle Excel-specific options
            if "sheet_name" in parsing_options:
                return parse_excel_sheet(file_path, parsing_options["sheet_name"], **parsing_options)
            else:
                return parse_excel(file_path, **parsing_options)
                
        else:
            # Default parsing
            return parse_file(file_path, file_format, **parsing_options)
            
    except Exception as e:
        logger.error(f"Failed to parse file with advanced options {file_path}: {str(e)}")
        raise Exception(f"Advanced file parsing failed: {str(e)}")


def get_supported_formats() -> List[str]:
    """
    Get list of supported file formats.
    
    Returns:
        List[str]: List of supported format strings
    """
    return ["csv", "json", "xml", "xls", "xlsx", "excel"]


def detect_file_format(file_path: str) -> str:
    """
    Detect file format based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Detected file format
    """
    import os
    
    _, ext = os.path.splitext(file_path.lower())
    
    format_mapping = {
        '.csv': 'csv',
        '.json': 'json',
        '.xml': 'xml',
        '.xls': 'excel',
        '.xlsx': 'excel',
        '.rss': 'xml',
        '.atom': 'xml'
    }
    
    return format_mapping.get(ext, 'unknown')


def validate_parsing_config(config: Dict[str, Any]) -> bool:
    """
    Validate parsing configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["format"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate format
    format_type = config.get("format", "").lower()
    if format_type not in get_supported_formats():
        return False
    
    return True