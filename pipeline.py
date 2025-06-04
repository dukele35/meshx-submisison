"""Data transformation pipeline for applying sequences of transformations.

This module provides a DataTransformationPipeline class that processes pandas DataFrames
through a sequence of registered transformations.
"""

import pandas as pd
from typing import Dict, Any, List
from registry import TransformationRegistry


class DataTransformationPipeline:
    """Pipeline for applying a sequence of data transformations.
    
    This class processes DataFrames through a configurable sequence of transformations
    using functions registered in a TransformationRegistry.
    
    Attributes:
        registry: TransformationRegistry instance containing available transformations
    """
    
    def __init__(self, registry: TransformationRegistry):
        """Initialize the pipeline with a transformation registry.
        
        Args:
            registry: TransformationRegistry containing available transformations
        """
        self.registry = registry
    
    def process(self, df: pd.DataFrame, pipeline_config: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process a DataFrame through a sequence of transformations.
        
        Each transformation in the pipeline is applied sequentially to the result
        of the previous transformation.
        
        Args:
            df: Input DataFrame to transform
            pipeline_config: List of transformation steps, each containing:
                           - 'type': Name of the transformation to apply
                           - 'config': Configuration dict for the transformation
                           
        Returns:
            Transformed DataFrame after applying all pipeline steps
            
        Raises:
            ValueError: If a transformation type is not found or disabled
        """
        result_df = df.copy()
        
        for step in pipeline_config:
            transformation_name = step['type']
            transformation_config = step.get('config', {})
            
            transformation_func = self.registry.get_transformation(transformation_name)
            result_df = transformation_func(result_df, transformation_config)
        
        return result_df