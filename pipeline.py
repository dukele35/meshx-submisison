import pandas as pd
from typing import Dict, Any, List
from registry import TransformationRegistry


class DataTransformationPipeline:
    def __init__(self, registry: TransformationRegistry):
        self.registry = registry
    
    def process(self, df: pd.DataFrame, pipeline_config: List[Dict[str, Any]]) -> pd.DataFrame:
        result_df = df.copy()
        
        for step in pipeline_config:
            transformation_name = step['type']
            transformation_config = step.get('config', {})
            
            transformation_func = self.registry.get_transformation(transformation_name)
            result_df = transformation_func(result_df, transformation_config)
        
        return result_df