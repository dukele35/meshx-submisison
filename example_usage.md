# Data Transformation System Usage Examples

## Running the API

```bash
cd api
pip install -r requirements.txt
python api.py
```

Or with Docker:
```bash
cd api
docker build -t data-transform .
docker run -p 5000:5000 data-transform
```

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:9999/health
```

### 2. Get Available Transformations
```bash
curl http://localhost:9999/transformations
```

### 3. Enable/Disable Transformations
```bash
curl -X POST http://localhost:5000/transformations/filter_rows/enable \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### 4. Transform Data
```bash
curl -X POST http://localhost:5000/transform \
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