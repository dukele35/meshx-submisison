"""Registry for managing data transformation functions.

This module provides a TransformationRegistry class that allows registration,
enabling/disabling, and retrieval of data transformation functions for pandas DataFrames.
"""

import pandas as pd
from typing import Dict, Any, List, Callable


class TransformationRegistry:
    """A registry for managing data transformation functions.
    
    This class provides a centralized way to register, enable/disable, and retrieve
    transformation functions that can be applied to pandas DataFrames.
    
    Attributes:
        _transformations: Dictionary mapping transformation names to functions
        _enabled_transformations: Dictionary tracking which transformations are enabled
    """
    
    def __init__(self):
        """Initialize the transformation registry with default transformations."""
        self._transformations: Dict[str, Callable] = {}
        self._enabled_transformations: Dict[str, bool] = {}
        self._register_default_transformations()
    
    def register(self, name: str, func: Callable, enabled: bool = True):
        """Register a new transformation function.
        
        Args:
            name: Unique name for the transformation
            func: Callable that takes (df, config) and returns transformed DataFrame
            enabled: Whether the transformation should be enabled by default
        """
        self._transformations[name] = func
        self._enabled_transformations[name] = enabled
    
    def enable(self, name: str, enabled: bool = True):
        """Enable or disable a registered transformation.
        
        Args:
            name: Name of the transformation to enable/disable
            enabled: True to enable, False to disable
        """
        if name in self._transformations:
            self._enabled_transformations[name] = enabled
    
    def get_transformation(self, name: str) -> Callable:
        """Get a transformation function by name.
        
        Args:
            name: Name of the transformation to retrieve
            
        Returns:
            The transformation function
            
        Raises:
            ValueError: If transformation not found or disabled
        """
        if name not in self._transformations:
            raise ValueError(f"Transformation '{name}' not found")
        if not self._enabled_transformations.get(name, False):
            raise ValueError(f"Transformation '{name}' is disabled")
        return self._transformations[name]
    
    def get_available_transformations(self) -> List[str]:
        """Get list of all enabled transformation names.
        
        Returns:
            List of enabled transformation names
        """
        return [name for name, enabled in self._enabled_transformations.items() if enabled]
    
    def _register_default_transformations(self):
        """Register the default set of transformations."""
        self.register('filter_rows', self._filter_rows)
        self.register('map_column', self._map_column)
        self.register('uppercase_column', self._uppercase_column)
    
    @staticmethod
    def _filter_rows(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Filter DataFrame rows based on column values.
        
        Args:
            df: Input DataFrame to filter
            config: Configuration with 'column', 'operator', and 'value' keys
                   Supported operators: ==, !=, >, <, >=, <=, contains
                   
        Returns:
            Filtered DataFrame
            
        Raises:
            ValueError: If operator is not supported
        """
        column = config['column']
        operator = config.get('operator', '==')
        value = config['value']
        
        if operator == '==':
            return df[df[column] == value]
        elif operator == '!=':
            return df[df[column] != value]
        elif operator == '>':
            return df[df[column] > value]
        elif operator == '<':
            return df[df[column] < value]
        elif operator == '>=':
            return df[df[column] >= value]
        elif operator == '<=':
            return df[df[column] <= value]
        elif operator == 'contains':
            return df[df[column].astype(str).str.contains(str(value), na=False)]
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    @staticmethod
    def _map_column(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Rename a column in the DataFrame.
        
        Args:
            df: Input DataFrame
            config: Configuration with 'old_name' and 'new_name' keys
                   
        Returns:
            DataFrame with renamed column
            
        Raises:
            ValueError: If the old column name doesn't exist
        """
        old_name = config['old_name']
        new_name = config['new_name']
        
        if old_name not in df.columns:
            raise ValueError(f"Column '{old_name}' not found in dataframe")
        
        df_copy = df.copy()
        df_copy = df_copy.rename(columns={old_name: new_name})
        return df_copy
    
    @staticmethod
    def _uppercase_column(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Convert all values in a column to uppercase.
        
        Args:
            df: Input DataFrame
            config: Configuration with 'column' key specifying column to uppercase
                   
        Returns:
            DataFrame with specified column values converted to uppercase
            
        Raises:
            ValueError: If the specified column doesn't exist
        """
        column = config['column']
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
        
        df_copy = df.copy()
        df_copy[column] = df_copy[column].astype(str).str.upper()
        return df_copy