from flask_restful import Resource
from flasgger.utils import swag_from


class HealthCheck(Resource):
    def get(self):
        """
        Health Check Endpoint
        ---
        tags:
          - Health
        responses:
          200:
            description: API is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return {'status': 'healthy'}