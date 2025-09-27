"""
Excel parser for converting Excel files to pandas DataFrames.
"""
import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Union


def parse_excel(file_path: str, **kwargs) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Parse Excel file into pandas DataFrame(s).
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments to pass to pd.read_excel()
        
    Returns:
        pd.DataFrame or Dict[str, pd.DataFrame]: Parsed Excel data
        
    Raises:
        Exception: If parsing fails
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Parsing Excel file: {file_path}")
        
        # Default parameters for Excel parsing
        default_params = {
            'engine': 'openpyxl',
            'na_values': ['', 'N/A', 'n/a', 'NULL', 'null', 'NaN', 'nan']
        }
        
        # Merge with user-provided parameters
        params = {**default_params, **kwargs}
        
        # Check if sheet_name is specified
        sheet_name = params.get('sheet_name', None)
        
        if sheet_name is None:
            # Read all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None, **params)
            logger.info(f"Successfully parsed Excel: {len(excel_data)} sheets")
            return excel_data
        else:
            # Read specific sheet
            df = pd.read_excel(file_path, **params)
            logger.info(f"Successfully parsed Excel: {len(df)} rows, {len(df.columns)} columns")
            return df
        
    except Exception as e:
        logger.error(f"Failed to parse Excel file {file_path}: {str(e)}")
        raise Exception(f"Excel parsing failed: {str(e)}")


def parse_excel_sheet(file_path: str, sheet_name: str, **kwargs) -> pd.DataFrame:
    """
    Parse specific sheet from Excel file.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to parse
        **kwargs: Additional arguments to pass to pd.read_excel()
        
    Returns:
        pd.DataFrame: Parsed Excel sheet data
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Parsing Excel sheet '{sheet_name}' from: {file_path}")
        
        # Default parameters
        default_params = {
            'engine': 'openpyxl',
            'sheet_name': sheet_name,
            'na_values': ['', 'N/A', 'n/a', 'NULL', 'null', 'NaN', 'nan']
        }
        
        # Merge with user-provided parameters
        params = {**default_params, **kwargs}
        
        # Read specific sheet
        df = pd.read_excel(file_path, **params)
        
        logger.info(f"Successfully parsed Excel sheet: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse Excel sheet '{sheet_name}' from {file_path}: {str(e)}")
        raise Exception(f"Excel sheet parsing failed: {str(e)}")


def parse_excel_with_header(file_path: str, header_row: int = 0, **kwargs) -> pd.DataFrame:
    """
    Parse Excel file with custom header row.
    
    Args:
        file_path: Path to the Excel file
        header_row: Row number to use as header (0-indexed)
        **kwargs: Additional arguments to pass to pd.read_excel()
        
    Returns:
        pd.DataFrame: Parsed Excel data with custom header
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Parsing Excel file with header row {header_row}: {file_path}")
        
        # Default parameters
        default_params = {
            'engine': 'openpyxl',
            'header': header_row,
            'na_values': ['', 'N/A', 'n/a', 'NULL', 'null', 'NaN', 'nan']
        }
        
        # Merge with user-provided parameters
        params = {**default_params, **kwargs}
        
        # Read Excel file
        df = pd.read_excel(file_path, **params)
        
        logger.info(f"Successfully parsed Excel with custom header: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse Excel file with header row {header_row} from {file_path}: {str(e)}")
        raise Exception(f"Excel parsing with custom header failed: {str(e)}")


def get_excel_sheet_names(file_path: str) -> List[str]:
    """
    Get list of sheet names in Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        List[str]: List of sheet names
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Getting sheet names from: {file_path}")
        
        # Read Excel file to get sheet names
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = excel_file.sheet_names
        
        logger.info(f"Found {len(sheet_names)} sheets: {sheet_names}")
        return sheet_names
        
    except Exception as e:
        logger.error(f"Failed to get sheet names from {file_path}: {str(e)}")
        raise Exception(f"Failed to get Excel sheet names: {str(e)}")


def parse_excel_with_schema(file_path: str, schema: Dict[str, Any]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Parse Excel file with a predefined schema.
    
    Args:
        file_path: Path to the Excel file
        schema: Dictionary defining parsing options for each sheet
        
    Returns:
        pd.DataFrame or Dict[str, pd.DataFrame]: Parsed Excel data with applied schema
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Parsing Excel file with schema: {file_path}")
        
        # Get sheet names
        sheet_names = get_excel_sheet_names(file_path)
        
        # Parse each sheet according to schema
        if len(sheet_names) == 1 and sheet_names[0] not in schema:
            # Single sheet, use default schema
            sheet_name = sheet_names[0]
            sheet_schema = schema.get('default', {})
            return parse_excel_sheet(file_path, sheet_name, **sheet_schema)
        else:
            # Multiple sheets or specific sheet schemas
            result = {}
            for sheet_name in sheet_names:
                sheet_schema = schema.get(sheet_name, schema.get('default', {}))
                result[sheet_name] = parse_excel_sheet(file_path, sheet_name, **sheet_schema)
            
            return result
        
    except Exception as e:
        logger.error(f"Failed to parse Excel file with schema {file_path}: {str(e)}")
        raise Exception(f"Excel parsing with schema failed: {str(e)}")


def validate_excel_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate and analyze Excel file structure.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dict: Structure analysis including sheet names, dimensions, etc.
    """
    logger = logging.getLogger("parser.excel")
    
    try:
        logger.info(f"Validating Excel structure: {file_path}")
        
        # Get sheet names
        sheet_names = get_excel_sheet_names(file_path)
        
        structure_info = {
            "sheet_count": len(sheet_names),
            "sheet_names": sheet_names
        }
        
        # Analyze each sheet
        sheet_info = {}
        for sheet_name in sheet_names:
            try:
                df = parse_excel_sheet(file_path, sheet_name, nrows=0)  # Read only headers
                sheet_info[sheet_name] = {
                    "columns": list(df.columns),
                    "column_count": len(df.columns)
                }
            except Exception as e:
                sheet_info[sheet_name] = {"error": str(e)}
        
        structure_info["sheets"] = sheet_info
        
        return structure_info
        
    except Exception as e:
        logger.error(f"Failed to validate Excel structure {file_path}: {str(e)}")
        raise Exception(f"Excel structure validation failed: {str(e)}")