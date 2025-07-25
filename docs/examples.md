# MCP Server Tool Examples

This document provides comprehensive examples of how to use each tool in the Python MCP Server. These examples help GitHub Copilot understand expected usage patterns and generate better suggestions.

## Code Execution Tool

### Basic Usage
```python
# Execute simple Python code
result = run_python("print('Hello, World!')")
# Returns: {"status": "success", "result": {"stdout": "Hello, World!\n", "stderr": "", "returncode": 0}}

# Execute code with variables
result = run_python("""
x = 10
y = 20
print(f"Sum: {x + y}")
""")

# Execute code with imports
result = run_python("""
import math
print(f"Pi: {math.pi}")
print(f"Square root of 16: {math.sqrt(16)}")
""")
```

### Data Analysis Example
```python
result = run_python("""
import pandas as pd
import numpy as np

# Create sample data
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data)
print(df.to_string())
print(f"Average age: {df['Age'].mean()}")
""")
```

## Linting Tool

### Basic Linting
```python
# Lint code with issues
result = lint_python("""
def hello( ):
    print( "hello world" )
    x=1+2
""")
# Returns issues about formatting, spacing, etc.

# Lint clean code
result = lint_python("""
def hello():
    print("hello world")
    x = 1 + 2
    return x
""")
```

## Formatting Tool

### Code Formatting
```python
# Format messy code
result = format_python("""
def calculate(x,y):
    return x+y

result=calculate(1,2)
print(result)
""")
# Returns formatted version with proper spacing
```

## Testing Tool

### Auto-generate Tests
```python
# Generate tests for a function
result = test_python("""
def add(a, b):
    '''Add two numbers together.'''
    return a + b

def multiply(x, y):
    '''Multiply two numbers.'''
    return x * y
""")
# Generates pytest test file and runs tests
```

### Test with Edge Cases
```python
result = test_python("""
def divide(a, b):
    '''Divide a by b, handling zero division.'''
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
# Generates tests including zero division case
```

## Documentation Generation

### Generate Docstrings
```python
result = generate_docs("""
def process_data(data):
    cleaned = data.strip()
    return cleaned.upper()

class DataProcessor:
    def __init__(self, config):
        self.config = config
        
    def process(self, items):
        return [self.process_item(item) for item in items]
""")
# Adds comprehensive docstrings to functions and classes
```

## Cloud SDK Examples

### AWS S3 Operations
```python
# Upload file to S3
result = aws_upload_s3({
    "bucket": "my-bucket",
    "key": "data/file.txt",
    "content": "Hello, S3!",
    "content_type": "text/plain"
})

# List S3 objects
result = aws_list_s3({"bucket": "my-bucket", "prefix": "data/"})
```

### GCP Storage Operations
```python
# List GCP bucket contents
result = gcp_list_bucket({
    "bucket_name": "my-gcp-bucket",
    "prefix": "uploads/"
})

# Upload to GCP
result = gcp_upload_blob({
    "bucket_name": "my-gcp-bucket", 
    "source_file": "local_file.txt",
    "destination_blob": "remote_file.txt"
})
```

### Azure Blob Operations
```python
# Download from Azure Blob
result = azure_download_blob({
    "container": "my-container",
    "blob_name": "data.json",
    "local_path": "/tmp/downloaded_data.json"
})

# Upload to Azure Blob
result = azure_upload_blob({
    "container": "my-container",
    "blob_name": "upload.txt",
    "data": "Content to upload"
})
```

## HTTP API Usage

### Using with curl
```bash
# Run Python code via HTTP
curl -X POST http://localhost:8080/run_code \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello from HTTP!\")"}'

# Lint code via HTTP
curl -X POST http://localhost:8080/lint_code \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello( ): print( \"hello\" )"}'

# Format code via HTTP
curl -X POST http://localhost:8080/format_code \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello():print(\"hello\")"}'
```

### Using with JavaScript
```javascript
// Run Python code from JavaScript
const response = await fetch('http://localhost:8080/run_code', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    code: 'import math\nprint(f"Pi is {math.pi}")'
  })
});
const result = await response.json();
console.log(result);
```

## Error Handling Patterns

### Handling Execution Errors
```python
# Code that will fail
result = run_python("""
import non_existent_module
print("This won't run")
""")
# Returns: {"status": "error", "error": "...", "traceback": "..."}

# Code with runtime error
result = run_python("""
x = 1 / 0
""")
# Returns error with traceback
```

### Handling Timeout
```python
# Code that takes too long
result = run_python("""
import time
time.sleep(60)  # Will timeout after 30 seconds
""")
# Returns timeout error
```
