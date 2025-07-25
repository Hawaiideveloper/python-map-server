
# Python MCP Server

A comprehensive Python MCP (Model Context Protocol) server with AI/LLM integration, system intelligence, and advanced development tools. This platform provides everything you need for Python development, machine learning, data science, and intelligent automation.

_This MCP server essentially gives you a comprehensive code quality and compliance toolkit that can analyze any Python repository and ensure it meets professional standards!_

## 🌟 Key Features

### 🚀 Core Development Tools
- **Safe Code Execution**: Sandboxed Python execution with resource limits
- **Code Quality**: Integrated linting (ruff), formatting (black), testing (pytest)
- **Documentation**: Automatic documentation generation
- **Intelligent Debugging**: AI-powered error analysis and fix suggestions

### 🤖 AI/LLM Integration
- **Multi-Model Chat**: OpenAI GPT, Anthropic Claude support
- **Vector Operations**: Embeddings, semantic search, vector databases
- **Machine Learning**: Scikit-learn, PyTorch, TensorFlow integration
- **NLP & Computer Vision**: Text analysis, image processing, OCR
- **100+ AI/ML Libraries**: Comprehensive ecosystem support

### 🧠 System Intelligence
- **Code Analysis**: AST parsing, complexity metrics, security scanning
- **System Monitoring**: CPU, memory, disk usage tracking
- **Project Scaffolding**: Intelligent project structure generation
- **Smart Debugging**: Automated error diagnosis and resolution

### ☁️ Cloud & Data Integration
- **Cloud SDKs**: AWS, GCP, Azure native integration
- **Databases**: PostgreSQL, MongoDB, Redis, SQLite support
- **Vector Databases**: ChromaDB, Pinecone, Qdrant, Weaviate
- **Data Science**: Pandas, NumPy, Matplotlib, Plotly, and more

## 📦 Supported Libraries (100+)

**Data Science**: numpy, pandas, matplotlib, seaborn, plotly, scipy, statsmodels  
**Machine Learning**: scikit-learn, torch, tensorflow, xgboost, lightgbm  
**AI/LLM**: openai, anthropic, langchain, transformers, sentence-transformers  
**NLP**: spacy, nltk, textblob, gensim  
**Computer Vision**: opencv-python, mediapipe  
**Vector DBs**: chromadb, pinecone-client, qdrant-client, weaviate-client  
**Web**: fastapi, requests, beautifulsoup4, selenium  
**Cloud**: boto3, google-cloud-*, azure-*  
**MLOps**: mlflow, wandb  
**And many more...

## 🚀 Quick Start

### Using Poetry (Recommended)

```bash
git clone <repo-url>
cd python-mcp-server
chmod +x setup.sh
./setup.sh                    # Automated setup script
poetry shell                  # Activate environment
poetry run python -m mcp_server.server  # Start server
```

### Manual Installation

```bash
git clone <repo-url>
cd python-mcp-server
poetry install
cp .env.example .env          # Configure environment
# Edit .env with your API keys
poetry run python -m mcp_server.server
```

### Using Docker

```bash
docker build -t python-mcp-server .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  python-mcp-server
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure your environment:

```bash
# AI/LLM APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PINECONE_API_KEY=your_pinecone_key
WANDB_API_KEY=your_wandb_key

# Cloud Providers
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
GCP_PROJECT=your_gcp_project
AZURE_STORAGE_CONNECTION_STRING=your_azure_string

# Database
DATABASE_URL=sqlite:///./mcp_server.db

# Security & Auth
JWT_SECRET_KEY=your_secret_key
API_RATE_LIMIT=100

# Vector Databases
CHROMA_PERSIST_DIRECTORY=./chroma_db
QDRANT_URL=http://localhost:6333
```

## 🛠️ API Endpoints

### Core Development Tools
- `POST /run_code` - Execute Python code safely
- `POST /lint_code` - Lint code with ruff
- `POST /format_code` - Format code with black
- `POST /test_code` - Run tests with pytest
- `POST /doc_gen` - Generate documentation

### AI/LLM Integration
- `POST /ai/chat` - Chat with OpenAI/Anthropic models
- `POST /ai/embeddings` - Create text embeddings
- `POST /ai/vector_search` - Search vector databases
- `POST /ai/train_model` - Train ML models
- `POST /ai/analyze_text` - NLP analysis
- `POST /ai/analyze_image` - Computer vision analysis

### System Intelligence
- `POST /system/info` - System monitoring & info
- `POST /system/code_intelligence` - Advanced code analysis
- `POST /system/debug` - Smart debugging assistance
- `POST /system/scaffold` - Generate project structures

### Cloud SDKs
- `POST /sdk/aws_upload_s3` - AWS S3 operations
- `POST /sdk/gcp_list_bucket` - GCP storage operations
- `POST /sdk/azure_download_blob` - Azure blob operations

## 💡 Usage Examples

### AI Chat
```python
import requests

response = requests.post("http://localhost:8080/ai/chat", json={
    "prompt": "Explain machine learning in simple terms",
    "model": "gpt-4",
    "provider": "openai"
})
```

### Code Analysis
```python
response = requests.post("http://localhost:8080/system/code_intelligence", json={
    "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "analysis_type": "comprehensive"
})
```

### Vector Search
```python
response = requests.post("http://localhost:8080/ai/vector_search", json={
    "query": "machine learning algorithms",
    "collection": "documents",
    "top_k": 5
})
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │────│  Python MCP      │────│  Tool Modules   │
│  (OpenAI/Claude)│    │     Server       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │                          │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   HTTP Bridge    │────│  AI/LLM Tools   │
                       │   (FastAPI)      │    │  Vector DBs     │
                       └──────────────────┘    │  Cloud SDKs     │
                                               │  System Intel   │
                                               └─────────────────┘
```

## 🔐 Security Features

- **Sandboxed Execution**: Safe code execution with resource limits
- **Import Filtering**: Allow 100+ safe libraries, block dangerous ones
- **Rate Limiting**: Configurable API rate limits
- **Authentication**: JWT-based API authentication
- **Audit Logging**: Complete operation audit trail
- **Input Validation**: Comprehensive sanitization

## 📊 Monitoring

- **System Metrics**: CPU, memory, disk usage
- **Performance Tracking**: Execution time monitoring
- **Error Analytics**: Detailed error reporting
- **Usage Statistics**: API endpoint analytics
- **Security Events**: Security incident tracking

## 🚀 Development

### Poetry Commands
```bash
poetry install              # Install dependencies
poetry shell               # Activate environment
poetry run pytest          # Run tests
poetry run ruff check .     # Lint code
poetry run black .          # Format code
poetry run jupyter lab      # Start Jupyter
```

### Testing
```bash
poetry run pytest tests/           # Run all tests
poetry run pytest --cov=src       # Run with coverage
poetry run pytest -v tests/test_ai_tools.py  # Specific module
```

## 🤖 GitHub Copilot Ready

This repository is optimized for GitHub Copilot:
- Comprehensive context files
- Detailed code patterns
- Type hints throughout
- Consistent architecture

## 📚 Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **API Reference**: Available at `/docs` when server is running
- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **Copilot Guide**: [.github/copilot-instructions.md](.github/copilot-instructions.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow code patterns and add tests
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Poetry](https://python-poetry.org/) for dependency management
- [FastAPI](https://fastapi.tiangolo.com/) for HTTP API
- All the amazing Python libraries that make this possible

---

**Ready to supercharge your Python development with AI? Get started now! 🚀**
