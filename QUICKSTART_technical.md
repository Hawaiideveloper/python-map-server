# 🚀 Quick Start Guide: Your Python MCP Server (For Beginners!)

## What is this thing? 🤔

Think of your Python MCP Server like a **magic toolbox** that can:
- ✏️ Write Python code for you
- 🔍 Check if your code is good (linting)
- ✨ Make your code pretty (formatting)
- 🏃‍♂️ Run your Python code safely
- 🧪 Test your code to make sure it works
- ☁️ Talk to cloud services like AWS and Google
- 🤖 Do AI/ML stuff like text analysis

It's like having a super smart coding assistant that lives on your computer!

## Step 1: Check if you have the right tools 🛠️

First, make sure you have these installed on your computer:

### Check Python (you need Python 3.8 or newer):
```bash
python3 --version
```
Should show something like: `Python 3.13.2` ✅

### Check Poetry (this manages your Python packages):
```bash
poetry --version
```
Should show something like: `Poetry (version 1.8.0)` ✅

**Don't have Poetry?** Install it:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Step 2: Get your server ready 🎯

### Navigate to your project:
```bash
cd /Users/hawaiidevelopergmail.com/Documents/github/python-mcp-server
```

### Install all the magic ingredients:
```bash
poetry install
```
*This downloads all the special Python packages your server needs. Like getting all the LEGO pieces before building!*

```bash
poetry shell
```
*This is like putting on special gloves that let you use all your tools properly.*

## Step 3: Start your magic server! 🎪

```bash
poetry run python -m mcp_server.server
```

You should see something like:
```
🚀 MCP Server starting...
🔑 Admin Key: mcp_admin_ABC123...
🔑 User Key: mcp_user_XYZ789...
📡 Server running on http://localhost:8000
```

**Important:** Save those keys! You'll need them to talk to your server.

## Step 4: Test if it's working 🧪

Open a new terminal (keep the server running in the first one) and try:

### Test 1: Run some Python code
```bash
curl -X POST http://localhost:8000/run_code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_KEY_HERE" \
  -d '{"code": "print(\"Hello World!\")"}'
```

Should return:
```json
{
  "stdout": "Hello World!\n",
  "stderr": "",
  "returncode": 0
}
```

### Test 2: Check code quality
```bash
curl -X POST http://localhost:8000/lint_code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_KEY_HERE" \
  -d '{"code": "def hello():    print(\"hi\")"}'
```

### Test 3: Format messy code
```bash
curl -X POST http://localhost:8000/format_code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_KEY_HERE" \
  -d '{"code": "def hello():print(\"hi\")"}'
```

## What can your server do? 🎁

Here are all the cool things you can ask your server to do:

### 🏃‍♂️ **Run Python Code**
- **What it does:** Runs Python code safely in a sandbox
- **Endpoint:** `POST /run_code`
- **Use case:** Test code snippets quickly

### 🔍 **Check Code Quality (Lint)**
- **What it does:** Finds problems in your code
- **Endpoint:** `POST /lint_code`
- **Use case:** Make sure your code follows best practices

### ✨ **Format Code**
- **What it does:** Makes your code look pretty and consistent
- **Endpoint:** `POST /format_code`
- **Use case:** Clean up messy code automatically

### 🧪 **Test Code**
- **What it does:** Creates and runs tests for your functions
- **Endpoint:** `POST /test_code`
- **Use case:** Make sure your code works correctly

### 📚 **Generate Documentation**
- **What it does:** Adds helpful comments to your code
- **Endpoint:** `POST /generate_docs`
- **Use case:** Make your code easier to understand

### ☁️ **Cloud Services**
- **What it does:** Upload files to AWS S3, list Google Cloud files, etc.
- **Endpoints:** `/aws_upload_s3`, `/gcp_list_bucket`
- **Use case:** Work with cloud storage

### 🤖 **AI/ML Tools**
- **What it does:** Analyze text, extract keywords, sentiment analysis
- **Endpoint:** `POST /ai_analyze`
- **Use case:** Smart text processing

## How to use it in your code 🎯

### Python Example:
```python
import requests

# Your server info
server_url = "http://localhost:8000"
api_key = "YOUR_USER_KEY_HERE"

# Headers for authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Run some Python code
response = requests.post(
    f"{server_url}/run_code",
    headers=headers,
    json={"code": "print('Hello from Python!')"}
)

result = response.json()
print(result["stdout"])  # Hello from Python!
```

### JavaScript Example:
```javascript
const serverUrl = "http://localhost:8000";
const apiKey = "YOUR_USER_KEY_HERE";

async function runPythonCode(code) {
    const response = await fetch(`${serverUrl}/run_code`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({ code: code })
    });
    
    const result = await response.json();
    return result.stdout;
}

// Use it
runPythonCode("print('Hello from JavaScript!')").then(console.log);
```

## Troubleshooting 🔧

### Server won't start?
1. Make sure you're in the right folder
2. Run `poetry install` again
3. Check if port 8000 is already used: `lsof -i :8000`

### Getting 403 Forbidden errors?
- Make sure you're using the correct API key in the `Authorization` header
- The key should start with `mcp_user_` or `mcp_admin_`

### Code execution fails?
- The server runs code in a safe sandbox with timeouts
- Very long-running code (>10 seconds) will be stopped
- Some system operations might not work in the sandbox

## Security Notes 🔒

- **API Keys:** Keep your keys secret! Don't share them or put them in code you upload to GitHub
- **Sandbox:** Code runs in a protected environment, but still be careful what you execute
- **Local Only:** Right now this only works on your computer. For cloud deployment, you'll need additional setup

## What's Next? 🌟

1. **Play around:** Try different code snippets and see what happens
2. **Build something:** Use the server in your own projects
3. **Explore AI features:** Try text analysis and ML tools
4. **Cloud setup:** When ready, we can help you deploy this to the cloud

## Need Help? 🆘

1. **Check the logs:** Look at what the server prints when it's running
2. **Test with curl:** Use the examples above to test each feature
3. **Read the code:** Look in `src/mcp_server/tools/` to see how each tool works

---

**Remember:** This server is like a powerful toolbox. Start with simple things (like running "Hello World") and gradually try more complex features. Have fun exploring! 🎉
- **Notebooks**: jupyter, ipykernel
- **Code Quality**: ruff, black, mypy, safety
- **Geographic**: geopandas, folium
- **Financial**: yfinance, alpha-vantage

## 🛠️ Usage Examples

### 1. Basic Code Execution
```python
# POST /run_code
{
  "code": "import pandas as pd\ndf = pd.DataFrame({'a': [1,2,3]})\nprint(df.head())"
}
```

### 2. AI Chat
```python
# POST /ai/chat
{
  "prompt": "Explain quantum computing in simple terms",
  "model": "gpt-4",
  "provider": "openai"
}
```

### 3. Vector Search
```python
# POST /ai/vector_search
{
  "query": "machine learning algorithms",
  "collection": "documents",
  "top_k": 5,
  "vector_db": "chromadb"
}
```

### 4. System Analysis
```python
# POST /system/info
# Returns comprehensive system information

# POST /system/code_intelligence
{
  "code": "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "analysis_type": "comprehensive"
}
```

### 5. Smart Debugging
```python
# POST /system/debug
{
  "code": "def buggy_function():\n    x = [1, 2, 3\n    return x[5]",
  "error_message": "IndexError: list index out of range"
}
```

### 6. Project Scaffolding
```python
# POST /system/scaffold
{
  "project_name": "my_ml_project",
  "project_type": "ml",
  "features": ["jupyter", "mlflow", "docker"]
}
```

## 🔧 Poetry Commands

```bash
# Environment management
poetry install                    # Install dependencies
poetry shell                     # Activate virtual environment
poetry add package-name          # Add new dependency
poetry add --group dev package   # Add dev dependency

# Development
poetry run python -m mcp_server.server    # Start server
poetry run pytest                         # Run tests
poetry run ruff check .                   # Lint code
poetry run black .                        # Format code
poetry run jupyter lab                    # Start Jupyter

# Build and deploy
poetry build                     # Build package
poetry publish                   # Publish to PyPI
```

## 🔐 Security Features

- **Code Sandboxing**: Safe execution with resource limits
- **Import Filtering**: Block dangerous imports, allow 100+ safe libraries
- **Rate Limiting**: Configurable API rate limits
- **Authentication**: JWT-based API authentication
- **Input Validation**: Comprehensive input sanitization
- **Audit Logging**: Complete audit trail of all operations

## 📈 Monitoring & Observability

- **Comprehensive Logging**: Structured logging with rotation
- **Performance Metrics**: Execution time tracking
- **System Monitoring**: CPU, memory, disk usage
- **Error Tracking**: Detailed error reporting with context
- **Rate Limit Monitoring**: API usage tracking

## 🌐 HTTP API Endpoints

### Core Tools
- `POST /run_code` - Execute Python code
- `POST /lint_code` - Lint Python code
- `POST /format_code` - Format Python code
- `POST /test_code` - Run Python tests
- `POST /doc_gen` - Generate documentation

### AI/LLM Tools
- `POST /ai/chat` - Chat with AI models
- `POST /ai/embeddings` - Create text embeddings
- `POST /ai/vector_search` - Search vector databases
- `POST /ai/train_model` - Train ML models
- `POST /ai/analyze_text` - Text analysis (NLP)
- `POST /ai/analyze_image` - Image analysis (CV)

### System Intelligence
- `POST /system/info` - System information
- `POST /system/code_intelligence` - Code analysis
- `POST /system/debug` - Smart debugging
- `POST /system/scaffold` - Project scaffolding

### Cloud SDKs
- `POST /sdk/aws_upload_s3` - AWS S3 operations
- `POST /sdk/gcp_list_bucket` - GCP storage operations
- `POST /sdk/azure_download_blob` - Azure blob operations

## 🤖 GitHub Copilot Integration

This repository is optimized for GitHub Copilot with:
- Comprehensive context in `.copilot/context.md`
- Detailed patterns in `.github/copilot-instructions.md`
- Type hints and documentation for better suggestions
- Consistent code patterns across all modules

## 🚀 Advanced Features

### 1. Multi-Model AI Support
- Switch between OpenAI and Anthropic
- Fallback mechanisms for reliability
- Cost optimization strategies

### 2. Vector Database Flexibility
- Support for 4+ vector databases
- Automatic collection management
- Hybrid search capabilities

### 3. MLOps Integration
- Experiment tracking with MLflow/Wandb
- Model versioning and deployment
- Automated hyperparameter tuning

### 4. Intelligent Code Analysis
- AST-based code analysis
- Security vulnerability detection
- Performance optimization suggestions
- Complexity metrics and reporting

## 🔧 Configuration

All configuration is handled through environment variables in `.env`:

- **API Keys**: OpenAI, Anthropic, Pinecone, etc.
- **Database URLs**: PostgreSQL, MongoDB, Redis
- **Cloud Credentials**: AWS, GCP, Azure
- **Security Settings**: JWT secrets, rate limits
- **Server Configuration**: Host, port, debug mode

## 📚 Learning Resources

- **MCP Protocol**: https://modelcontextprotocol.io/
- **Poetry**: https://python-poetry.org/docs/
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the established patterns
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to build amazing Python applications with AI superpowers? Let's get started! 🚀**
