from flask import Flask, request
from flask_restful import Api, Resource
import pandas as pd
import io
import json
from registry import TransformationRegistry
from pipeline import DataTransformationPipeline


app = Flask(__name__)
api = Api(app)
registry = TransformationRegistry()
pipeline = DataTransformationPipeline(registry)


class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy'}


class Transformations(Resource):
    def get(self):
        return {
            'available_transformations': registry.get_available_transformations()
        }


class TransformationToggle(Resource):
    def post(self, name):
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        try:
            registry.enable(name, enabled)
            return {'success': True, 'message': f"Transformation '{name}' {'enabled' if enabled else 'disabled'}"}
        except Exception as e:
            return {'error': str(e)}, 400


class Transform(Resource):
    def post(self):
        try:
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            if not file.filename.endswith('.csv'):
                return {'error': 'Only CSV files are supported'}, 400
            
            pipeline_config_str = request.form.get('pipeline')
            if not pipeline_config_str:
                return {'error': 'No pipeline configuration provided'}, 400
            
            try:
                pipeline_config = json.loads(pipeline_config_str)
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON in pipeline configuration'}, 400
            
            csv_content = file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            
            transformed_df = pipeline.process(df, pipeline_config)
            
            result = {
                'original_shape': list(df.shape),
                'transformed_shape': list(transformed_df.shape),
                'data': transformed_df.to_dict('records')
            }
            
            return result
        
        except Exception as e:
            return {'error': str(e)}, 500


api.add_resource(HealthCheck, '/health')
api.add_resource(Transformations, '/transformations')
api.add_resource(TransformationToggle, '/transformations/<string:name>/enable')
api.add_resource(Transform, '/transform')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)