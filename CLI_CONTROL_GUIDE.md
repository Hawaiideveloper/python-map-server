# Railway MCP Server Command Line Control

This guide shows you how to control the deployed MCP server on Railway using command line tools.

## 🛠️ Available CLI Tools

### 1. Bash CLI Script (`railway-mcp-cli.sh`)
Simple bash script for basic operations without dependencies.

### 2. Python CLI (`railway-mcp-cli.py`)
Advanced Python CLI with WebSocket testing and interactive mode.

### 3. Railway CLI (Official)
Official Railway CLI for infrastructure management.

---

## 🚀 Quick Start

### Install Railway CLI (Optional)
```bash
curl -fsSL https://railway.app/install.sh | sh
railway login
```

### Make scripts executable
```bash
chmod +x railway-mcp-cli.sh
chmod +x railway-mcp-cli.py
```

---

## 📋 Command Examples

### Basic Status Check
```bash
# Using bash script
./railway-mcp-cli.sh status

# Using Python CLI
python3 railway-mcp-cli.py status
```

### Execute Python Code
```bash
# Simple execution
./railway-mcp-cli.sh exec "print('Hello from Railway!')"

# With file
python3 railway-mcp-cli.py exec --file my_script.py

# With timeout
python3 railway-mcp-cli.py exec --code "import time; time.sleep(5); print('Done')" --timeout 10
```

### Code Quality
```bash
# Lint code
./railway-mcp-cli.sh lint my_file.py
python3 railway-mcp-cli.py lint --file my_file.py

# Format code
./railway-mcp-cli.sh format my_file.py
```

### System Information
```bash
# Get system info
./railway-mcp-cli.sh system
python3 railway-mcp-cli.py system
```

### WebSocket MCP Testing
```bash
# Test WebSocket MCP protocol
python3 railway-mcp-cli.py ws-test
```

### Interactive Mode
```bash
# Start interactive session
python3 railway-mcp-cli.py --interactive
```

### Deployment Control
```bash
# Trigger new deployment
./railway-mcp-cli.sh deploy
python3 railway-mcp-cli.py deploy

# Scale service (requires Railway CLI)
railway scale --replicas 2

# View logs (requires Railway CLI)
railway logs --tail 100
```

---

## 🔧 Advanced Usage

### 1. Bash Script Commands
```bash
./railway-mcp-cli.sh <command> [options]

Commands:
  status              Check server health
  info                Get server information
  tools               List available tools
  exec <code>         Execute Python code
  lint <file>         Lint Python code
  format <file>       Format Python code
  system              Get system information
  deploy              Trigger deployment
  logs                View logs (requires Railway CLI)
  scale <replicas>    Scale service (requires Railway CLI)
```

### 2. Python CLI Commands
```bash
python3 railway-mcp-cli.py <command> [options]

Commands:
  status              Check server health
  info                Get server information
  system              Get system information
  exec                Execute Python code
  lint                Lint Python code
  ws-test             Test WebSocket MCP
  deploy              Trigger deployment
  
Options:
  --code <code>       Python code to execute/lint
  --file <file>       File to process
  --timeout <sec>     Execution timeout
  --interactive       Interactive mode
```

### 3. Interactive Mode
```bash
python3 railway-mcp-cli.py --interactive

# Available commands in interactive mode:
mcp> status          # Check status
mcp> system          # System info
mcp> exec print('hi') # Execute code
mcp> ws-test         # Test WebSocket
mcp> deploy          # Trigger deployment
mcp> exit            # Quit
```

---

## 🌐 Railway Infrastructure Commands

### Using Official Railway CLI
```bash
# Login to Railway
railway login

# Link to project (if needed)
railway link

# View service status
railway status

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# View logs
railway logs --tail 100

# Scale service
railway scale --replicas 2

# Deploy current code
railway deploy

# Open Railway dashboard
railway open
```

---

## 🔗 WebSocket MCP Testing

### Test WebSocket Connection
```bash
# Using Python CLI
python3 railway-mcp-cli.py ws-test

# Using wscat (if installed)
wscat -c wss://python-mcp-server-production.up.railway.app/mcp

# Send initialize message
{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0","capabilities":{}},"id":1}
```

---

## 📊 Monitoring and Debugging

### Check Server Health
```bash
# Quick health check
curl -s -H "X-Admin-Key: mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs" \
  "https://python-mcp-server-production.up.railway.app/health" | jq

# Detailed server info
./railway-mcp-cli.sh info
```

### View Logs
```bash
# Railway logs (requires Railway CLI)
railway logs --tail 100

# Application logs via API
curl -s -H "X-Admin-Key: mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs" \
  "https://python-mcp-server-production.up.railway.app/system/logs"
```

### Performance Monitoring
```bash
# System information
./railway-mcp-cli.sh system

# Resource usage
python3 railway-mcp-cli.py system
```

---

## 🔐 Authentication

All API requests require the admin key:
```
X-Admin-Key: mcp_admin_Pyef86sg2Vj36zS2-I8k-LWH5rSGVj859oErBeAy-Cs
```

The CLI tools automatically include this header for all requests.

---

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```bash
   # Check server status
   ./railway-mcp-cli.sh status
   ```

2. **Authentication Failed**
   ```bash
   # Verify admin key is correct
   grep ADMIN_KEY railway-mcp-cli.sh
   ```

3. **WebSocket Connection Failed**
   ```bash
   # Test WebSocket endpoint
   python3 railway-mcp-cli.py ws-test
   ```

4. **Deployment Issues**
   ```bash
   # Check Railway deployment status
   railway status
   railway logs
   ```

---

## 📈 Performance Tips

1. **Use timeouts** for long-running code execution
2. **Monitor resource usage** with system commands
3. **Scale replicas** during high load periods
4. **Use interactive mode** for multiple operations
5. **Check logs regularly** for error patterns

---

## 🎯 Integration Examples

### CI/CD Pipeline
```bash
#!/bin/bash
# Deploy and test
./railway-mcp-cli.sh deploy
sleep 60  # Wait for deployment
./railway-mcp-cli.sh status
python3 railway-mcp-cli.py ws-test
```

### Development Workflow
```bash
# Test code locally then on server
python3 my_script.py
./railway-mcp-cli.sh exec "$(cat my_script.py)"
./railway-mcp-cli.sh lint my_script.py
```

### Monitoring Script
```bash
#!/bin/bash
while true; do
  ./railway-mcp-cli.sh status
  ./railway-mcp-cli.sh system
  sleep 300  # Check every 5 minutes
done
```

---

This gives you complete command-line control over your Railway-deployed MCP server! 🚀
