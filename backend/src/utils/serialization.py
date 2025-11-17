"""
Utility functions for JSON serialization
Converts NumPy types to native Python types
"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List


def convert_to_serializable(obj: Any) -> Any:
    """
    Recursively convert NumPy/Pandas types to native Python types
    for JSON serialization
    
    Args:
        obj: Any object that might contain NumPy types
    
    Returns:
        Object with all NumPy types converted to native Python types
    """
    if isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        return str(obj)
    
    elif isinstance(obj, np.bool_):
        return bool(obj)
    
    elif pd.isna(obj):
        return None
    
    else:
        return obj


def sanitize_indicators(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize indicators dictionary for JSON serialization
    
    Args:
        indicators: Dictionary of calculated indicators
    
    Returns:
        Sanitized dictionary with all values JSON-serializable
    """
    return convert_to_serializable(indicators)


def sanitize_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize entire API response for JSON serialization
    
    Args:
        response: Complete API response dictionary
    
    Returns:
        Sanitized response ready for JSON serialization
    """
    return convert_to_serializable(response)