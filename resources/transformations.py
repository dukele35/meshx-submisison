from flask import request
from flask_restful import Resource
from registry import TransformationRegistry

registry = TransformationRegistry()


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