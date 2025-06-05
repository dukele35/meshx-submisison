from flask import request
from flask_restful import Resource
import pandas as pd
import io
import json
import mimetypes
import os
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
            
            # File type validation
            if not file.filename.lower().endswith('.csv'):
                return {'error': 'Only CSV files are supported'}, 400
            
            # MIME type validation
            mime_type, _ = mimetypes.guess_type(file.filename)
            if mime_type and mime_type not in ['text/csv', 'text/plain', 'application/csv']:
                return {'error': 'Invalid file type. Expected CSV format'}, 400
            
            # File size validation (10MB limit)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if file_size > MAX_FILE_SIZE:
                return {'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}, 400
            
            if file_size == 0:
                return {'error': 'Empty file provided'}, 400
            
            pipeline_config_str = request.form.get('pipeline')
            if not pipeline_config_str:
                return {'error': 'No pipeline configuration provided'}, 400
            
            try:
                pipeline_config = json.loads(pipeline_config_str)
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON in pipeline configuration'}, 400
            
            # Handle both old and new pipeline formats
            if isinstance(pipeline_config, dict) and 'steps' in pipeline_config:
                # Old format: {"steps": [{"name": "...", "params": {...}}]}
                steps = pipeline_config['steps']
                if not isinstance(steps, list):
                    return {'error': 'Pipeline steps must be a list'}, 400
                # Convert to new format
                pipeline_config = []
                for step in steps:
                    if not isinstance(step, dict):
                        return {'error': 'Each step must be an object'}, 400
                    if 'name' not in step:
                        return {'error': 'Step missing required "name" field'}, 400
                    pipeline_config.append({
                        'type': step['name'],
                        'config': step.get('params', {})
                    })
            
            # Validate pipeline structure
            if not isinstance(pipeline_config, list):
                return {'error': 'Pipeline must be a list of transformation steps'}, 400
            
            if len(pipeline_config) == 0:
                return {'error': 'Pipeline cannot be empty'}, 400
            
            if len(pipeline_config) > 10:
                return {'error': 'Pipeline cannot have more than 10 steps'}, 400
            
            # Validate each transformation step
            for i, step in enumerate(pipeline_config):
                if not isinstance(step, dict):
                    return {'error': f'Step {i+1}: Each step must be an object'}, 400
                
                if 'type' not in step:
                    return {'error': f'Step {i+1}: Missing required "type" field'}, 400
                
                if not isinstance(step['type'], str):
                    return {'error': f'Step {i+1}: "type" must be a string'}, 400
                
                if 'config' not in step:
                    return {'error': f'Step {i+1}: Missing required "config" field'}, 400
                
                if not isinstance(step['config'], dict):
                    return {'error': f'Step {i+1}: "config" must be an object'}, 400
                
                # Check for unexpected fields
                allowed_fields = {'type', 'config'}
                unexpected = set(step.keys()) - allowed_fields
                if unexpected:
                    return {'error': f'Step {i+1}: Unexpected fields: {", ".join(unexpected)}'}, 400
            
            # Read and validate CSV content
            csv_content = file.read().decode('utf-8')
            
            # Basic malicious content scanning
            suspicious_patterns = [
                '<?php', '<%', '<script', 'eval(', 'exec(', 'system(', 
                'subprocess', 'import os', '__import__', 'open('
            ]
            
            content_lower = csv_content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    return {'error': 'File contains potentially malicious content'}, 400
            
            # Validate CSV structure
            try:
                df = pd.read_csv(io.StringIO(csv_content))
            except pd.errors.EmptyDataError:
                return {'error': 'CSV file is empty or has no valid data'}, 400
            except pd.errors.ParserError as e:
                return {'error': f'Invalid CSV format: {str(e)}'}, 400
            except UnicodeDecodeError:
                return {'error': 'File encoding is not valid UTF-8'}, 400
            
            # Validate CSV has data
            if df.empty:
                return {'error': 'CSV file contains no data rows'}, 400
            
            # Validate reasonable column count (prevent memory exhaustion)
            if len(df.columns) > 100:
                return {'error': 'CSV file has too many columns (max 100)'}, 400
            
            transformed_df = pipeline.process(df, pipeline_config)
            
            result = {
                'original_shape': list(df.shape),
                'transformed_shape': list(transformed_df.shape),
                'data': transformed_df.to_dict('records')
            }
            
            return result
        
        except Exception as e:
            return {'error': str(e)}, 500