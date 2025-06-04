from flask import request
from flask_restful import Resource
import pandas as pd
import io
import json
from common import TransformationRegistry, DataTransformationPipeline

registry = TransformationRegistry()
pipeline = DataTransformationPipeline(registry)


class Transform(Resource):
    def post(self):
        """
        Transform CSV Data
        ---
        tags:
          - Transform
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: CSV file to transform
          - name: pipeline
            in: formData
            type: string
            required: true
            description: JSON configuration for transformation pipeline
            example: '{"steps": [{"name": "normalize", "params": {}}]}'
        responses:
          200:
            description: Data transformed successfully
            schema:
              type: object
              properties:
                original_shape:
                  type: array
                  items:
                    type: integer
                  example: [100, 5]
                transformed_shape:
                  type: array
                  items:
                    type: integer
                  example: [100, 5]
                data:
                  type: array
                  items:
                    type: object
          400:
            description: Bad request - missing file or invalid parameters
            schema:
              type: object
              properties:
                error:
                  type: string
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                error:
                  type: string
        """
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