from flask import Flask
from flask_restful import Api
from resources import HealthCheck, Transformations, TransformationToggle, Transform


app = Flask(__name__)
api = Api(app)

api.add_resource(HealthCheck, '/health')
api.add_resource(Transformations, '/transformations')
api.add_resource(TransformationToggle, '/transformations/<string:name>/enable')
api.add_resource(Transform, '/transform')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)