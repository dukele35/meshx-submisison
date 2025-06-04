import pandas as pd
from typing import Dict, Any, List, Callable


class TransformationRegistry:
    def __init__(self):
        self._transformations: Dict[str, Callable] = {}
        self._enabled_transformations: Dict[str, bool] = {}
        self._register_default_transformations()
    
    def register(self, name: str, func: Callable, enabled: bool = True):
        self._transformations[name] = func
        self._enabled_transformations[name] = enabled
    
    def enable(self, name: str, enabled: bool = True):
        if name in self._transformations:
            self._enabled_transformations[name] = enabled
    
    def get_transformation(self, name: str) -> Callable:
        if name not in self._transformations:
            raise ValueError(f"Transformation '{name}' not found")
        if not self._enabled_transformations.get(name, False):
            raise ValueError(f"Transformation '{name}' is disabled")
        return self._transformations[name]
    
    def get_available_transformations(self) -> List[str]:
        return [name for name, enabled in self._enabled_transformations.items() if enabled]
    
    def _register_default_transformations(self):
        self.register('filter_rows', self._filter_rows)
        self.register('map_column', self._map_column)
        self.register('uppercase_column', self._uppercase_column)
    
    @staticmethod
    def _filter_rows(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
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
        old_name = config['old_name']
        new_name = config['new_name']
        
        if old_name not in df.columns:
            raise ValueError(f"Column '{old_name}' not found in dataframe")
        
        df_copy = df.copy()
        df_copy = df_copy.rename(columns={old_name: new_name})
        return df_copy
    
    @staticmethod
    def _uppercase_column(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        column = config['column']
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
        
        df_copy = df.copy()
        df_copy[column] = df_copy[column].astype(str).str.upper()
        return df_copy