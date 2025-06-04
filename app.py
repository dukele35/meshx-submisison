import logging
import time
from flask import Flask, request, g
from flask_restful import Api
from waitress import serve
from resources import HealthCheck, Transformations, TransformationToggle, Transform

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
api = Api(app)

@app.before_request
def before_request():
    g.start_time = time.time()
    app.logger.info(f'Request: {request.method} {request.url} - IP: {request.remote_addr}')

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f'Response: {response.status_code} - Duration: {duration:.3f}s')
    return response

api.add_resource(HealthCheck, '/health')
api.add_resource(Transformations, '/transformations')
api.add_resource(TransformationToggle, '/transformations/<string:name>/enable')
api.add_resource(Transform, '/transform')


if __name__ == '__main__':
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    app.logger.info('Starting Flask application with Waitress server')
    serve(app, host='0.0.0.0', port=5001, url_scheme='http', threads=4)