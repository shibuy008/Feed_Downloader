"""
Decompressor utility for handling compressed files (ZIP, GZIP, TAR).
"""
import os
import zipfile
import gzip
import tarfile
import logging
from typing import List, Optional, Dict, Any


def decompress(file_path: str, compression_type: str = "auto", extract_to: str = None) -> List[str]:
    """
    Decompress a file based on compression type.
    
    Args:
        file_path: Path to the compressed file
        compression_type: Type of compression (zip, gzip, tar, auto)
        extract_to: Directory to extract to (defaults to same directory as file)
        
    Returns:
        List[str]: List of extracted file paths
        
    Raises:
        Exception: If decompression fails
    """
    logger = logging.getLogger("decompressor")
    
    try:
        # Auto-detect compression type if not specified
        if compression_type == "auto":
            compression_type = _detect_compression_type(file_path)
        
        # Set extraction directory
        if extract_to is None:
            extract_to = os.path.dirname(file_path)
        
        # Ensure extraction directory exists
        os.makedirs(extract_to, exist_ok=True)
        
        logger.info(f"Decompressing {file_path} ({compression_type}) to {extract_to}")
        
        if compression_type == "zip":
            return _decompress_zip(file_path, extract_to)
        elif compression_type == "gzip":
            return _decompress_gzip(file_path, extract_to)
        elif compression_type == "tar":
            return _decompress_tar(file_path, extract_to)
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")
            
    except Exception as e:
        logger.error(f"Failed to decompress {file_path}: {str(e)}")
        raise Exception(f"Decompression failed: {str(e)}")


def _decompress_zip(file_path: str, extract_to: str) -> List[str]:
    """
    Decompress ZIP file.
    
    Args:
        file_path: Path to ZIP file
        extract_to: Directory to extract to
        
    Returns:
        List[str]: List of extracted file paths
    """
    logger = logging.getLogger("decompressor")
    extracted_files = []
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Get list of files in archive
            file_list = zip_ref.namelist()
            
            # Extract all files
            zip_ref.extractall(extract_to)
            
            # Build list of extracted file paths
            for file_name in file_list:
                extracted_path = os.path.join(extract_to, file_name)
                if os.path.isfile(extracted_path):
                    extracted_files.append(extracted_path)
            
            logger.info(f"Extracted {len(extracted_files)} files from ZIP")
            return extracted_files
            
    except Exception as e:
        logger.error(f"ZIP decompression failed: {str(e)}")
        raise Exception(f"ZIP decompression failed: {str(e)}")


def _decompress_gzip(file_path: str, extract_to: str) -> List[str]:
    """
    Decompress GZIP file.
    
    Args:
        file_path: Path to GZIP file
        extract_to: Directory to extract to
        
    Returns:
        List[str]: List of extracted file paths
    """
    logger = logging.getLogger("decompressor")
    
    try:
        # Determine output filename
        base_name = os.path.basename(file_path)
        if base_name.endswith('.gz'):
            output_name = base_name[:-3]  # Remove .gz extension
        else:
            output_name = base_name + '.decompressed'
        
        output_path = os.path.join(extract_to, output_name)
        
        # Decompress file
        with gzip.open(file_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        logger.info(f"Extracted GZIP file to {output_path}")
        return [output_path]
        
    except Exception as e:
        logger.error(f"GZIP decompression failed: {str(e)}")
        raise Exception(f"GZIP decompression failed: {str(e)}")


def _decompress_tar(file_path: str, extract_to: str) -> List[str]:
    """
    Decompress TAR file.
    
    Args:
        file_path: Path to TAR file
        extract_to: Directory to extract to
        
    Returns:
        List[str]: List of extracted file paths
    """
    logger = logging.getLogger("decompressor")
    extracted_files = []
    
    try:
        with tarfile.open(file_path, "r:*") as tar_ref:
            # Get list of members
            members = tar_ref.getmembers()
            
            # Extract all files
            tar_ref.extractall(extract_to)
            
            # Build list of extracted file paths
            for member in members:
                if member.isfile():
                    extracted_path = os.path.join(extract_to, member.name)
                    if os.path.isfile(extracted_path):
                        extracted_files.append(extracted_path)
            
            logger.info(f"Extracted {len(extracted_files)} files from TAR")
            return extracted_files
            
    except Exception as e:
        logger.error(f"TAR decompression failed: {str(e)}")
        raise Exception(f"TAR decompression failed: {str(e)}")


def _detect_compression_type(file_path: str) -> str:
    """
    Auto-detect compression type based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Detected compression type
    """
    _, ext = os.path.splitext(file_path.lower())
    
    compression_mapping = {
        '.zip': 'zip',
        '.gz': 'gzip',
        '.tar': 'tar',
        '.tar.gz': 'tar',
        '.tgz': 'tar',
        '.tar.bz2': 'tar',
        '.tbz2': 'tar'
    }
    
    return compression_mapping.get(ext, 'unknown')


def list_archive_contents(file_path: str, compression_type: str = "auto") -> List[Dict[str, Any]]:
    """
    List contents of compressed archive without extracting.
    
    Args:
        file_path: Path to the compressed file
        compression_type: Type of compression
        
    Returns:
        List[Dict]: List of archive contents with metadata
    """
    logger = logging.getLogger("decompressor")
    
    try:
        # Auto-detect compression type if not specified
        if compression_type == "auto":
            compression_type = _detect_compression_type(file_path)
        
        if compression_type == "zip":
            return _list_zip_contents(file_path)
        elif compression_type == "tar":
            return _list_tar_contents(file_path)
        else:
            logger.warning(f"Cannot list contents for compression type: {compression_type}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to list archive contents: {str(e)}")
        raise Exception(f"Failed to list archive contents: {str(e)}")


def _list_zip_contents(file_path: str) -> List[Dict[str, Any]]:
    """
    List ZIP archive contents.
    
    Args:
        file_path: Path to ZIP file
        
    Returns:
        List[Dict]: List of file information
    """
    contents = []
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for info in zip_ref.infolist():
            contents.append({
                'filename': info.filename,
                'size': info.file_size,
                'compressed_size': info.compress_size,
                'is_dir': info.is_dir(),
                'date_time': info.date_time
            })
    
    return contents


def _list_tar_contents(file_path: str) -> List[Dict[str, Any]]:
    """
    List TAR archive contents.
    
    Args:
        file_path: Path to TAR file
        
    Returns:
        List[Dict]: List of file information
    """
    contents = []
    
    with tarfile.open(file_path, "r:*") as tar_ref:
        for member in tar_ref.getmembers():
            contents.append({
                'filename': member.name,
                'size': member.size,
                'is_dir': member.isdir(),
                'is_file': member.isfile(),
                'mtime': member.mtime,
                'mode': member.mode
            })
    
    return contents


def extract_specific_files(file_path: str, file_patterns: List[str], compression_type: str = "auto", extract_to: str = None) -> List[str]:
    """
    Extract only specific files from archive based on patterns.
    
    Args:
        file_path: Path to the compressed file
        file_patterns: List of filename patterns to match
        compression_type: Type of compression
        extract_to: Directory to extract to
        
    Returns:
        List[str]: List of extracted file paths
    """
    import fnmatch
    
    logger = logging.getLogger("decompressor")
    
    try:
        # Auto-detect compression type if not specified
        if compression_type == "auto":
            compression_type = _detect_compression_type(file_path)
        
        # Set extraction directory
        if extract_to is None:
            extract_to = os.path.dirname(file_path)
        
        # Ensure extraction directory exists
        os.makedirs(extract_to, exist_ok=True)
        
        extracted_files = []
        
        if compression_type == "zip":
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    # Check if file matches any pattern
                    if any(fnmatch.fnmatch(file_name, pattern) for pattern in file_patterns):
                        zip_ref.extract(file_name, extract_to)
                        extracted_path = os.path.join(extract_to, file_name)
                        if os.path.isfile(extracted_path):
                            extracted_files.append(extracted_path)
        
        elif compression_type == "tar":
            with tarfile.open(file_path, "r:*") as tar_ref:
                for member in tar_ref.getmembers():
                    # Check if file matches any pattern
                    if any(fnmatch.fnmatch(member.name, pattern) for pattern in file_patterns):
                        tar_ref.extract(member, extract_to)
                        extracted_path = os.path.join(extract_to, member.name)
                        if os.path.isfile(extracted_path):
                            extracted_files.append(extracted_path)
        
        logger.info(f"Extracted {len(extracted_files)} matching files")
        return extracted_files
        
    except Exception as e:
        logger.error(f"Failed to extract specific files: {str(e)}")
        raise Exception(f"Failed to extract specific files: {str(e)}")