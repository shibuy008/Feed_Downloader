"""
XML parser for converting XML files to pandas DataFrames.
"""
import xml.etree.ElementTree as ET
import xmltodict
import pandas as pd
import logging
from typing import Dict, Any, List, Optional


def parse_xml(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Parse XML file into a pandas DataFrame.
    
    Args:
        file_path: Path to the XML file
        **kwargs: Additional arguments for parsing options
        
    Returns:
        pd.DataFrame: Parsed XML data
        
    Raises:
        Exception: If parsing fails
    """
    logger = logging.getLogger("parser.xml")
    
    try:
        logger.info(f"Parsing XML file: {file_path}")
        
        # Parse XML to dictionary
        with open(file_path, 'r', encoding='utf-8') as f:
            data = xmltodict.parse(f.read())
        
        # Convert to DataFrame
        df = pd.json_normalize(data)
        
        logger.info(f"Successfully parsed XML: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse XML file {file_path}: {str(e)}")
        raise Exception(f"XML parsing failed: {str(e)}")


def parse_xml_with_xpath(file_path: str, xpath: str) -> pd.DataFrame:
    """
    Parse XML file and extract data using XPath.
    
    Args:
        file_path: Path to the XML file
        xpath: XPath expression to extract specific elements
        
    Returns:
        pd.DataFrame: Parsed XML data from XPath
    """
    logger = logging.getLogger("parser.xml")
    
    try:
        logger.info(f"Parsing XML file with XPath {xpath}: {file_path}")
        
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Find elements using XPath
        elements = root.findall(xpath)
        
        # Convert elements to list of dictionaries
        data = []
        for element in elements:
            element_dict = {}
            
            # Add attributes
            for attr_name, attr_value in element.attrib.items():
                element_dict[f"@{attr_name}"] = attr_value
            
            # Add text content
            if element.text and element.text.strip():
                element_dict["text"] = element.text.strip()
            
            # Add child elements
            for child in element:
                if len(child) == 0:  # Leaf element
                    if child.text and child.text.strip():
                        element_dict[child.tag] = child.text.strip()
                else:  # Nested element
                    element_dict[child.tag] = _element_to_dict(child)
            
            data.append(element_dict)
        
        # Convert to DataFrame
        if data:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()
        
        logger.info(f"Successfully parsed XML with XPath: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse XML file with XPath {file_path}: {str(e)}")
        raise Exception(f"XML parsing with XPath failed: {str(e)}")


def parse_xml_rss(file_path: str) -> pd.DataFrame:
    """
    Parse RSS/Atom feed XML file.
    
    Args:
        file_path: Path to the RSS/Atom XML file
        
    Returns:
        pd.DataFrame: Parsed RSS feed data
    """
    logger = logging.getLogger("parser.xml")
    
    try:
        logger.info(f"Parsing RSS/Atom feed: {file_path}")
        
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle different RSS/Atom formats
        items = []
        
        # RSS format
        if root.tag.endswith('rss'):
            for item in root.findall('.//item'):
                item_dict = _rss_item_to_dict(item)
                items.append(item_dict)
        
        # Atom format
        elif root.tag.endswith('feed'):
            for entry in root.findall('.//entry'):
                item_dict = _atom_entry_to_dict(entry)
                items.append(item_dict)
        
        # Convert to DataFrame
        if items:
            df = pd.DataFrame(items)
        else:
            df = pd.DataFrame()
        
        logger.info(f"Successfully parsed RSS/Atom feed: {len(df)} items")
        return df
        
    except Exception as e:
        logger.error(f"Failed to parse RSS/Atom feed {file_path}: {str(e)}")
        raise Exception(f"RSS/Atom parsing failed: {str(e)}")


def _element_to_dict(element) -> Dict[str, Any]:
    """
    Convert XML element to dictionary recursively.
    
    Args:
        element: XML element
        
    Returns:
        Dict: Element as dictionary
    """
    result = {}
    
    # Add attributes
    for attr_name, attr_value in element.attrib.items():
        result[f"@{attr_name}"] = attr_value
    
    # Add text content
    if element.text and element.text.strip():
        result["text"] = element.text.strip()
    
    # Add child elements
    for child in element:
        if child.tag in result:
            # Multiple elements with same tag
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(_element_to_dict(child))
        else:
            result[child.tag] = _element_to_dict(child)
    
    return result


def _rss_item_to_dict(item) -> Dict[str, Any]:
    """
    Convert RSS item element to dictionary.
    
    Args:
        item: RSS item element
        
    Returns:
        Dict: Item as dictionary
    """
    item_dict = {}
    
    for child in item:
        if child.text:
            item_dict[child.tag] = child.text.strip()
        else:
            # Handle nested elements
            item_dict[child.tag] = _element_to_dict(child)
    
    return item_dict


def _atom_entry_to_dict(entry) -> Dict[str, Any]:
    """
    Convert Atom entry element to dictionary.
    
    Args:
        entry: Atom entry element
        
    Returns:
        Dict: Entry as dictionary
    """
    entry_dict = {}
    
    for child in entry:
        if child.text:
            entry_dict[child.tag] = child.text.strip()
        else:
            # Handle nested elements
            entry_dict[child.tag] = _element_to_dict(child)
    
    return entry_dict


def validate_xml_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate and analyze XML file structure.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        Dict: Structure analysis including root element, namespaces, etc.
    """
    logger = logging.getLogger("parser.xml")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        structure_info = {
            "root_tag": root.tag,
            "namespaces": list(root.attrib.keys()) if root.attrib else [],
            "child_count": len(root),
            "has_text": bool(root.text and root.text.strip())
        }
        
        # Get unique child tags
        child_tags = set()
        for child in root:
            child_tags.add(child.tag)
        structure_info["child_tags"] = list(child_tags)
        
        return structure_info
        
    except Exception as e:
        logger.error(f"Failed to validate XML structure {file_path}: {str(e)}")
        raise Exception(f"XML structure validation failed: {str(e)}")