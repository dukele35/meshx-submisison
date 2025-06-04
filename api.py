from flask import Flask, request, jsonify
import pandas as pd
import io
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


app = Flask(__name__)
registry = TransformationRegistry()
pipeline = DataTransformationPipeline(registry)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@app.route('/transformations', methods=['GET'])
def get_available_transformations():
    return jsonify({
        'available_transformations': registry.get_available_transformations()
    })


@app.route('/transformations/<name>/enable', methods=['POST'])
def toggle_transformation(name):
    data = request.get_json()
    enabled = data.get('enabled', True)
    
    try:
        registry.enable(name, enabled)
        return jsonify({'success': True, 'message': f"Transformation '{name}' {'enabled' if enabled else 'disabled'}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/transform', methods=['POST'])
def transform_data():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        pipeline_config_str = request.form.get('pipeline')
        if not pipeline_config_str:
            return jsonify({'error': 'No pipeline configuration provided'}), 400
        
        try:
            import json
            pipeline_config = json.loads(pipeline_config_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in pipeline configuration'}), 400
        
        csv_content = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        
        transformed_df = pipeline.process(df, pipeline_config)
        
        result = {
            'original_shape': list(df.shape),
            'transformed_shape': list(transformed_df.shape),
            'data': transformed_df.to_dict('records')
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)