"""
CSV parser for converting CSV files to pandas DataFrames.
"""
import pandas as pd
import logging
from typing import Dict, Any, Optional


def parse_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Parse CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file
        **kwargs: Additional arguments to pass to pd.read_csv()
        
    Returns:
        pd.DataFrame: Parsed CSV data
        
    Raises:
        Exception: If parsing fails
    """
    logger = logging.getLogger("parser.csv")
    
    try:
        logger.info(f"Parsing CSV file: {file_path}")
        
        # Default parameters for CSV parsing
        default_params = {
            'encoding': 'utf-8',
            'low_memory': False,
            'infer_datetime_format': True,
            'parse_dates': True
        }
        
        # Merge with user-provided parameters
        params = {**default_params, **kwargs}
        
        # Read CSV file
        df = pd.read_csv(file_path, **params)
        
        logger.info(f"Successfully parsed CSV: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse CSV file {file_path}: {str(e)}")
        raise Exception(f"CSV parsing failed: {str(e)}")


def parse_csv_with_schema(file_path: str, schema: Dict[str, Any]) -> pd.DataFrame:
    """
    Parse CSV file with a predefined schema.
    
    Args:
        file_path: Path to the CSV file
        schema: Dictionary defining column types and parsing options
        
    Returns:
        pd.DataFrame: Parsed CSV data with applied schema
    """
    logger = logging.getLogger("parser.csv")
    
    try:
        logger.info(f"Parsing CSV file with schema: {file_path}")
        
        # Extract parsing parameters from schema
        parse_params = schema.get('parse_params', {})
        column_types = schema.get('column_types', {})
        date_columns = schema.get('date_columns', [])
        
        # Set up date parsing
        if date_columns:
            parse_params['parse_dates'] = date_columns
        
        # Read CSV with parameters
        df = pd.read_csv(file_path, **parse_params)
        
        # Apply column type conversions
        for column, dtype in column_types.items():
            if column in df.columns:
                df[column] = df[column].astype(dtype)
        
        logger.info(f"Successfully parsed CSV with schema: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse CSV file with schema {file_path}: {str(e)}")
        raise Exception(f"CSV parsing with schema failed: {str(e)}")


def detect_csv_delimiter(file_path: str) -> str:
    """
    Detect the delimiter used in a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        str: Detected delimiter
    """
    import csv
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter
    except Exception:
        # Default to comma if detection fails
        return ','