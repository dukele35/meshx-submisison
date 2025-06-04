from flask import Flask, request, jsonify
import pandas as pd
import io
from registry import TransformationRegistry
from pipeline import DataTransformationPipeline



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