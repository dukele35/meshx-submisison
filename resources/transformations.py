from flask import request
from flask_restful import Resource
from common import TransformationRegistry

registry = TransformationRegistry()


class Transformations(Resource):
    def get(self):
        """
        Get Available Transformations
        ---
        tags:
          - Transformations
        responses:
          200:
            description: List of available transformations
            schema:
              type: object
              properties:
                available_transformations:
                  type: array
                  items:
                    type: string
                  example: ["normalize", "scale", "clean"]
        """
        return {
            'available_transformations': registry.get_available_transformations()
        }


class TransformationToggle(Resource):
    def post(self, name):
        """
        Enable/Disable Transformation
        ---
        tags:
          - Transformations
        parameters:
          - name: name
            in: path
            type: string
            required: true
            description: The transformation name
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                enabled:
                  type: boolean
                  example: true
        responses:
          200:
            description: Transformation toggled successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
          400:
            description: Error occurred
            schema:
              type: object
              properties:
                error:
                  type: string
        """
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        try:
            registry.enable(name, enabled)
            return {'success': True, 'message': f"Transformation '{name}' {'enabled' if enabled else 'disabled'}"}
        except Exception as e:
            return {'error': str(e)}, 400