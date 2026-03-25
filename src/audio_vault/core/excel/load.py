import pandas as pd
from pathlib import Path
from typing import Tuple, List, Optional


REQUIRED_COLUMNS = {"Songname", "Youtube link"}


def load_and_validate_excel(file_path: str) -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Load and validate an Excel file for required columns and data integrity.
    
    Handles files with or without headers. If no headers are found, assumes:
    - First column: Songname
    - Second column: Youtube link
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Tuple of (DataFrame or None, list of error/warning messages)
        If validation fails, DataFrame will be None and messages will contain errors.
    """
    errors = []
    
    try:
        # Check if file exists
        if not Path(file_path).exists():
            errors.append(f"File not found: {file_path}")
            return None, errors
        
        # Try to read the Excel file without assuming headers
        df = pd.read_excel(file_path, header=None)
        
    except Exception as e:
        errors.append(f"Failed to read Excel file: {str(e)}")
        return None, errors
    
    # Check if DataFrame is empty
    if df.empty:
        errors.append("Excel file is empty")
        return None, errors
    
    # Check if file has headers in the first row
    first_row = set(df.iloc[0].astype(str).str.strip().values)
    has_headers = REQUIRED_COLUMNS.issubset(first_row)
    
    if has_headers:
        # First row contains headers, reload with headers
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            errors.append(f"Failed to read Excel file with headers: {str(e)}")
            return None, errors
    else:
        # No headers found, assign them manually
        if len(df.columns) < 2:
            errors.append("Excel file must have at least 2 columns (Songname and Youtube link)")
            return None, errors
        
        df.columns = ["Songname", "Youtube link"]
    
    # Check for required columns
    file_columns = set(df.columns)
    missing_columns = REQUIRED_COLUMNS - file_columns
    
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return None, errors
    
    # Validate data integrity
    integrity_issues = _validate_data_integrity(df)
    errors.extend(integrity_issues)
    
    # If there are integrity issues, decline the file
    if integrity_issues:
        return None, errors
    
    return df, errors


def _validate_data_integrity(df: pd.DataFrame) -> List[str]:
    """
    Validate that each Songname has a Youtube link and vice versa.
    
    Args:
        df: DataFrame with Songname and Youtube link columns
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check for missing values in Songname column
    missing_songnames = df[df["Songname"].isna() | (df["Songname"].astype(str).str.strip() == "")]
    if not missing_songnames.empty:
        missing_indices = missing_songnames.index.tolist()
        errors.append(f"Found empty Songname values at row(s): {missing_indices}")
    
    # Check for missing values in Youtube link column
    missing_links = df[df["Youtube link"].isna() | (df["Youtube link"].astype(str).str.strip() == "")]
    if not missing_links.empty:
        missing_indices = missing_links.index.tolist()
        errors.append(f"Found empty Youtube link values at row(s): {missing_indices}")
    
    # Check for rows where Songname has value but Youtube link is empty
    songname_without_link = df[
        (df["Songname"].notna()) & 
        (df["Songname"].astype(str).str.strip() != "") &
        ((df["Youtube link"].isna()) | (df["Youtube link"].astype(str).str.strip() == ""))
    ]
    if not songname_without_link.empty:
        missing_indices = songname_without_link.index.tolist()
        errors.append(f"Found Songname(s) without Youtube link at row(s): {missing_indices}")
    
    # Check for rows where Youtube link has value but Songname is empty
    link_without_songname = df[
        ((df["Songname"].isna()) | (df["Songname"].astype(str).str.strip() == "")) &
        (df["Youtube link"].notna()) & 
        (df["Youtube link"].astype(str).str.strip() != "")
    ]
    if not link_without_songname.empty:
        missing_indices = link_without_songname.index.tolist()
        errors.append(f"Found Youtube link(s) without Songname at row(s): {missing_indices}")
    
    return errors
