"""
JSON parser for converting JSON files to pandas DataFrames.
"""
import json
import pandas as pd
import logging
from typing import Dict, Any, List, Union


def parse_json(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Parse JSON file into a pandas DataFrame.
    
    Args:
        file_path: Path to the JSON file
        **kwargs: Additional arguments to pass to pd.json_normalize() or pd.DataFrame()
        
    Returns:
        pd.DataFrame: Parsed JSON data
        
    Raises:
        Exception: If parsing fails
    """
    logger = logging.getLogger("parser.json")
    
    try:
        logger.info(f"Parsing JSON file: {file_path}")
        
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame based on data structure
        if isinstance(data, list):
            # List of objects
            if data and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                # List of primitives
                df = pd.DataFrame({"value": data})
        elif isinstance(data, dict):
            # Single object or nested structure
            try:
                # Try to normalize nested JSON
                df = pd.json_normalize(data, **kwargs)
            except Exception:
                # Fallback to simple DataFrame
                df = pd.DataFrame([data])
        else:
            # Primitive value
            df = pd.DataFrame([{"value": data}])
        
        logger.info(f"Successfully parsed JSON: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse JSON file {file_path}: {str(e)}")
        raise Exception(f"JSON parsing failed: {str(e)}")


def parse_json_stream(file_path: str) -> List[pd.DataFrame]:
    """
    Parse JSON Lines (JSONL) or streaming JSON file.
    
    Args:
        file_path: Path to the JSON Lines file
        
    Returns:
        List[pd.DataFrame]: List of DataFrames for each JSON object
    """
    logger = logging.getLogger("parser.json")
    
    try:
        logger.info(f"Parsing JSON Lines file: {file_path}")
        
        dataframes = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        df = pd.DataFrame([data] if isinstance(data, dict) else data)
                        dataframes.append(df)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {str(e)}")
                        continue
        
        logger.info(f"Successfully parsed JSON Lines: {len(dataframes)} objects")
        return dataframes
        
    except Exception as e:
        logger.error(f"Failed to parse JSON Lines file {file_path}: {str(e)}")
        raise Exception(f"JSON Lines parsing failed: {str(e)}")


def parse_json_with_path(file_path: str, json_path: str = None) -> pd.DataFrame:
    """
    Parse JSON file and extract data from a specific path.
    
    Args:
        file_path: Path to the JSON file
        json_path: JSONPath expression to extract specific data
        
    Returns:
        pd.DataFrame: Parsed JSON data from specified path
    """
    logger = logging.getLogger("parser.json")
    
    try:
        logger.info(f"Parsing JSON file with path {json_path}: {file_path}")
        
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract data from path if specified
        if json_path:
            # Simple path extraction (e.g., "data.items" or "results")
            path_parts = json_path.split('.')
            extracted_data = data
            
            for part in path_parts:
                if isinstance(extracted_data, dict) and part in extracted_data:
                    extracted_data = extracted_data[part]
                else:
                    logger.warning(f"Path {json_path} not found in JSON data")
                    return pd.DataFrame()
            
            data = extracted_data
        
        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
        else:
            df = pd.DataFrame([{"value": data}])
        
        logger.info(f"Successfully parsed JSON with path: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse JSON file with path {file_path}: {str(e)}")
        raise Exception(f"JSON parsing with path failed: {str(e)}")


def validate_json_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate and analyze JSON file structure.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict: Structure analysis including type, size, and schema info
    """
    logger = logging.getLogger("parser.json")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        structure_info = {
            "type": type(data).__name__,
            "size": len(data) if hasattr(data, '__len__') else 1
        }
        
        if isinstance(data, list) and data:
            structure_info["item_type"] = type(data[0]).__name__
            if isinstance(data[0], dict):
                structure_info["keys"] = list(data[0].keys())
        elif isinstance(data, dict):
            structure_info["keys"] = list(data.keys())
        
        return structure_info
        
    except Exception as e:
        logger.error(f"Failed to validate JSON structure {file_path}: {str(e)}")
        raise Exception(f"JSON structure validation failed: {str(e)}")