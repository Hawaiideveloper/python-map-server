# Python MCP Server - Developer Quickstart Guide

Welcome to the most comprehensive Python MCP (Model Context Protocol) server! This platform provides everything you need for Python development, AI/LLM integration, and intelligent automation.

## 🚀 Quick Setup

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd python-mcp-server
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the server:**
   ```bash
   poetry shell
   poetry run python -m mcp_server.server
   ```

## 🎯 Key Capabilities

### Core Development Tools
- **Code Execution**: Safe Python code execution with sandboxing
- **Code Quality**: Linting (ruff), formatting (black), testing (pytest)
- **Documentation**: Automatic documentation generation
- **Debugging**: Intelligent debugging assistance with error analysis

### AI/LLM Integration
- **Chat AI**: OpenAI GPT, Anthropic Claude integration
- **Embeddings**: Text-to-vector conversion for semantic search
- **Vector Search**: ChromaDB, Pinecone, Qdrant, Weaviate support
- **ML Training**: Scikit-learn, PyTorch, TensorFlow model training
- **NLP Analysis**: Sentiment, entity recognition, text classification
- **Computer Vision**: Image analysis, object detection, OCR

### System Intelligence
- **System Monitoring**: CPU, memory, disk usage tracking
- **Code Analysis**: AST parsing, complexity analysis, security scanning
- **Project Scaffolding**: Intelligent project structure generation
- **Smart Debugging**: Automated error diagnosis and fix suggestions

### Cloud & Data
- **Cloud SDKs**: AWS, GCP, Azure integration
- **Databases**: PostgreSQL, MongoDB, Redis, SQLite support
- **Data Science**: Pandas, NumPy, Matplotlib, Seaborn, Plotly
- **Time Series**: Prophet, statsmodels for forecasting

## 📊 Available Libraries (100+)

### Data Science & Analysis
- **Core**: numpy, pandas, matplotlib, seaborn, plotly
- **Statistics**: scipy, statsmodels, prophet
- **High Performance**: polars, dask

### Machine Learning & AI
- **Frameworks**: scikit-learn, torch, tensorflow, keras
- **LLMs**: openai, anthropic, langchain, transformers
- **Boosting**: xgboost, lightgbm
- **NLP**: spacy, nltk, textblob, gensim
- **Computer Vision**: opencv-python, mediapipe
- **Audio**: librosa, pydub

### Vector Databases
- **ChromaDB**: Local vector storage
- **Pinecone**: Cloud vector database
- **Qdrant**: High-performance vector search
- **Weaviate**: Knowledge graph + vectors
- **FAISS**: Facebook's similarity search

### Web & APIs
- **Frameworks**: fastapi, aiohttp
- **HTTP Clients**: requests, httpx
- **Web Scraping**: beautifulsoup4, selenium, scrapy
- **Authentication**: fastapi-users

### Cloud & Infrastructure
- **AWS**: boto3 for all AWS services
- **Google Cloud**: google-cloud-* libraries
- **Azure**: azure-* SDK
- **Database**: psycopg2, pymongo, redis

### Development & MLOps
- **Experiment Tracking**: mlflow, wandb
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
