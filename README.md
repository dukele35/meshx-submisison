# Data Transformation System

A Flask-based REST API for performing data transformations on CSV files with configurable pipeline support.

## Installation and Setup

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

### Docker Deployment

#### Quick Start with Docker Compose

```bash
# Run the main application
docker-compose up -d data-transformer

# Run with all services (Redis cache + Prometheus monitoring)
docker-compose --profile monitoring up -d

# View logs
docker-compose logs -f data-transformer

# Stop services
docker-compose down
```

#### Manual Docker Build

```bash
docker build -t data-transform .
docker run -p 5001:5001 data-transform
```

#### Docker Services

The Docker Compose setup includes:

- **data-transformer**: Main Flask application (port 5001)
- **redis**: Redis cache for future enhancements (port 6379) 
- **prometheus**: Monitoring and metrics collection (port 9090) - optional with `--profile monitoring`

#### Docker Features

- **Health checks**: Automatic container health monitoring
- **Non-root user**: Security best practices
- **Volume mounting**: Persistent logs and data
- **Network isolation**: Services communicate via dedicated network
- **Auto-restart**: Containers restart automatically on failure

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:5001/health
```

### 2. Get Available Transformations
```bash
curl http://localhost:5001/transformations
```

### 3. Enable/Disable Transformations
```bash
curl -X POST http://localhost:5001/transformations/filter_rows/enable \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 4. Transform Data
```bash
curl -X POST http://localhost:5001/transform \
  -F "file=@data.csv" \
  -F 'pipeline=[
    {
      "type": "filter_rows",
      "config": {
        "column": "age",
        "operator": ">",
        "value": 25
      }
    },
    {
      "type": "uppercase_column",
      "config": {
        "column": "name"
      }
    },
    {
      "type": "map_column",
      "config": {
        "old_name": "name",
        "new_name": "full_name"
      }
    }
  ]'
```

## Pipeline Configuration Format

The pipeline is defined as a JSON array of transformation steps:

```json
[
  {
    "type": "transformation_name",
    "config": {
      "parameter1": "value1",
      "parameter2": "value2"
    }
  }
]
```

## Available Transformations

### 1. filter_rows
Filters rows based on column values.

**Config parameters:**
- `column`: Column name to filter on
- `operator`: One of `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`
- `value`: Value to compare against

### 2. map_column (rename)
Renames a column.

**Config parameters:**
- `old_name`: Current column name
- `new_name`: New column name

### 3. uppercase_column
Converts string values in a column to uppercase.

**Config parameters:**
- `column`: Column name to transform

## Example CSV Data

Create a file `data.csv`:
```csv
name,age,city
john,30,New York
jane,22,Boston
bob,35,Chicago
alice,28,Seattle
```

The transformation pipeline above would:
1. Filter rows where age > 25
2. Convert names to uppercase
3. Rename "name" column to "full_name"

Result:
```json
{
  "original_shape": [4, 3],
  "transformed_shape": [3, 3],
  "data": [
    {"full_name": "JOHN", "age": 30, "city": "New York"},
    {"full_name": "BOB", "age": 35, "city": "Chicago"},
    {"full_name": "ALICE", "age": 28, "city": "Seattle"}
  ]
}
```

## API Documentation with Swagger

The application includes built-in Swagger documentation for interactive API exploration.

### Accessing Swagger UI

Once the application is running, navigate to:
```
http://localhost:5001/apidocs
```

The Swagger UI provides:
- Interactive API documentation
- Ability to test endpoints directly from the browser
- Request/response schemas and examples
- Parameter descriptions and validation rules

### Using Swagger UI

1. Start the application: `python app.py`
2. Open your browser and go to `http://localhost:5001/apidocs`
3. Explore available endpoints in the interactive interface
4. Click on any endpoint to see detailed documentation
5. Use the "Try it out" button to test endpoints with sample data
6. View response schemas and status codes

## Testing with pytest

The project includes comprehensive tests using pytest.

### Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py

# Run tests with coverage
pytest --cov=.

# Run tests and generate HTML coverage report
pytest --cov=. --cov-report=html
```

### Test Structure

- `tests/conftest.py`: Contains shared pytest fixtures
- `tests/test_health.py`: Tests for health check endpoint
- `tests/test_transform.py`: Tests for data transformation functionality
- `tests/test_transformations.py`: Tests for transformation management

### Available Test Fixtures

- `client`: Flask test client for making API requests
- `sample_csv_content`: Sample CSV data for testing transformations
- `empty_csv_content`: Empty CSV content for edge case testing

### Writing Tests

Tests use the Flask test client fixture to simulate HTTP requests:

```python
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
```

For file upload tests, use the sample CSV fixtures:

```python
def test_transform_with_data(client, sample_csv_content):
    data = {
        'file': (io.StringIO(sample_csv_content), 'test.csv'),
        'pipeline': json.dumps([...])
    }
    response = client.post('/transform', data=data)
    assert response.status_code == 200
```