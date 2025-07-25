# 🚀 Python Code Quality CI/CD

**One-click Python code quality and compliance for any repository**

Instantly add professional-grade code analysis, AI-powered insights, and automated quality checks to your GitHub repository using our Python MCP server.

## 🎯 What This Does

✅ **Automated Code Quality**: Linting, formatting, testing, documentation  
✅ **AI-Powered Analysis**: Code complexity, security scanning, intelligent suggestions  
✅ **Compliance Checking**: PEP 8, type hints, docstrings, best practices  
✅ **Performance Insights**: Code efficiency analysis and optimization tips  
✅ **Zero Setup**: Just copy our workflow file - that's it!  

## 🚀 Quick Setup (2 minutes)

### Step 1: Add GitHub Action

Copy this file to your repo: `.github/workflows/python-quality.yml`

```yaml
name: Python Code Quality & Compliance

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install MCP Server
      run: |
        pip install poetry
        git clone https://github.com/your-org/python-mcp-server.git /tmp/mcp-server
        cd /tmp/mcp-server
        poetry install
    
    - name: Run Code Quality Analysis
      run: |
        cd /tmp/mcp-server
        poetry run python .github/scripts/analyze-repo.py ${{ github.workspace }}
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        REPO_PATH: ${{ github.workspace }}
    
    - name: Upload Quality Report
      uses: actions/upload-artifact@v3
      with:
        name: code-quality-report
        path: quality-report.json
    
    - name: Comment PR (if applicable)
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = JSON.parse(fs.readFileSync('quality-report.json', 'utf8'));
          
          const comment = `## 🔍 Code Quality Report
          
          **Overall Score**: ${report.overall_score}/100 ${report.overall_score >= 80 ? '✅' : '⚠️'}
          
          ### 📊 Analysis Summary
          - **Linting Issues**: ${report.lint_issues} ${report.lint_issues === 0 ? '✅' : '❌'}
          - **Type Coverage**: ${report.type_coverage}% ${report.type_coverage >= 80 ? '✅' : '⚠️'}
          - **Test Coverage**: ${report.test_coverage}% ${report.test_coverage >= 80 ? '✅' : '⚠️'}
          - **Documentation**: ${report.doc_coverage}% ${report.doc_coverage >= 70 ? '✅' : '⚠️'}
          
          ### 🤖 AI Insights
          ${report.ai_suggestions.map(s => `- ${s}`).join('\n')}
          
          ### 🔒 Security
          ${report.security_issues.length === 0 ? '✅ No security issues found' : '❌ ' + report.security_issues.length + ' security issues detected'}
          
          [View Full Report](${report.detailed_report_url})`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### Step 2: Add Analysis Script

Create `.github/scripts/analyze-repo.py`:

```python
#!/usr/bin/env python3
"""
Repository analysis script for Python Code Quality CI/CD
Analyzes any Python repository and generates comprehensive quality reports
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze-repo.py <repo_path>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    if not repo_path.exists():
        print(f"Error: Repository path {repo_path} does not exist")
        sys.exit(1)
    
    print(f"🔍 Analyzing repository: {repo_path}")
    
    # Initialize report
    report = {
        "repository": str(repo_path),
        "analysis_timestamp": "",
        "overall_score": 0,
        "lint_issues": 0,
        "type_coverage": 0,
        "test_coverage": 0,
        "doc_coverage": 0,
        "ai_suggestions": [],
        "security_issues": [],
        "detailed_results": {}
    }
    
    # Run analysis using MCP server tools
    try:
        # 1. Lint Analysis
        print("📝 Running lint analysis...")
        lint_result = run_mcp_tool("lint_code", {
            "code_path": str(repo_path),
            "recursive": True
        })
        report["lint_issues"] = lint_result.get("issues_count", 0)
        report["detailed_results"]["lint"] = lint_result
        
        # 2. Type Checking
        print("🔍 Checking type annotations...")
        type_result = run_mcp_tool("analyze_types", {
            "code_path": str(repo_path)
        })
        report["type_coverage"] = type_result.get("coverage_percentage", 0)
        report["detailed_results"]["types"] = type_result
        
        # 3. Test Coverage
        print("🧪 Analyzing test coverage...")
        test_result = run_mcp_tool("analyze_tests", {
            "code_path": str(repo_path)
        })
        report["test_coverage"] = test_result.get("coverage_percentage", 0)
        report["detailed_results"]["tests"] = test_result
        
        # 4. Documentation Analysis
        print("📚 Checking documentation...")
        doc_result = run_mcp_tool("analyze_documentation", {
            "code_path": str(repo_path)
        })
        report["doc_coverage"] = doc_result.get("coverage_percentage", 0)
        report["detailed_results"]["documentation"] = doc_result
        
        # 5. AI-Powered Code Intelligence
        print("🤖 Running AI analysis...")
        ai_result = run_mcp_tool("ai_code_analysis", {
            "code_path": str(repo_path),
            "analysis_type": "comprehensive"
        })
        report["ai_suggestions"] = ai_result.get("suggestions", [])
        report["detailed_results"]["ai_analysis"] = ai_result
        
        # 6. Security Scanning
        print("🔒 Security scanning...")
        security_result = run_mcp_tool("security_scan", {
            "code_path": str(repo_path)
        })
        report["security_issues"] = security_result.get("issues", [])
        report["detailed_results"]["security"] = security_result
        
        # Calculate overall score
        report["overall_score"] = calculate_overall_score(report)
        
        # Save report
        with open("quality-report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Analysis complete! Overall score: {report['overall_score']}/100")
        
        # Generate summary
        generate_summary_report(report)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

def run_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Run an MCP server tool and return results"""
    import requests
    
    try:
        response = requests.post(
            f"http://localhost:8080/{tool_name}",
            json=params,
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Warning: Tool {tool_name} failed: {e}")
        return {}

def calculate_overall_score(report: Dict[str, Any]) -> int:
    """Calculate overall quality score (0-100)"""
    scores = []
    
    # Lint score (0-25 points)
    lint_score = max(0, 25 - report["lint_issues"])
    scores.append(min(25, lint_score))
    
    # Type coverage (0-25 points)
    type_score = (report["type_coverage"] / 100) * 25
    scores.append(type_score)
    
    # Test coverage (0-25 points)
    test_score = (report["test_coverage"] / 100) * 25
    scores.append(test_score)
    
    # Documentation (0-25 points)
    doc_score = (report["doc_coverage"] / 100) * 25
    scores.append(doc_score)
    
    return int(sum(scores))

def generate_summary_report(report: Dict[str, Any]):
    """Generate human-readable summary"""
    summary = f"""
# 📊 Python Code Quality Report

## Overall Score: {report['overall_score']}/100 {'✅' if report['overall_score'] >= 80 else '⚠️' if report['overall_score'] >= 60 else '❌'}

## 📈 Quality Metrics

| Metric | Score | Status |
|--------|-------|--------|
| Linting | {25 - min(25, report['lint_issues'])} issues | {'✅' if report['lint_issues'] == 0 else '❌'} |
| Type Coverage | {report['type_coverage']}% | {'✅' if report['type_coverage'] >= 80 else '⚠️'} |
| Test Coverage | {report['test_coverage']}% | {'✅' if report['test_coverage'] >= 80 else '⚠️'} |
| Documentation | {report['doc_coverage']}% | {'✅' if report['doc_coverage'] >= 70 else '⚠️'} |

## 🤖 AI Recommendations

{chr(10).join(f"- {suggestion}" for suggestion in report['ai_suggestions'][:5])}

## 🔒 Security Status

{f"✅ No security issues detected" if not report['security_issues'] else f"❌ {len(report['security_issues'])} security issues found"}

---
Generated by Python Code Quality CI/CD
    """
    
    with open("quality-summary.md", "w") as f:
        f.write(summary)

if __name__ == "__main__":
    main()
```

### Step 3: Configure (Optional)

Add `.github/quality-config.yml` for custom settings:

```yaml
# Python Code Quality CI/CD Configuration

# Quality thresholds
thresholds:
  overall_score: 80          # Minimum overall score
  lint_issues: 0             # Maximum lint issues
  type_coverage: 80          # Minimum type coverage %
  test_coverage: 80          # Minimum test coverage %
  doc_coverage: 70           # Minimum documentation %

# Analysis settings
analysis:
  ai_enabled: true           # Enable AI-powered analysis
  security_scan: true        # Run security scanning
  complexity_check: true     # Check code complexity
  performance_hints: true    # Performance optimization tips

# Reporting
reporting:
  comment_on_pr: true        # Comment quality report on PRs
  fail_on_threshold: false   # Fail CI if below threshold
  upload_artifacts: true     # Upload detailed reports
  generate_badge: true       # Generate quality badge

# Exclusions
exclude:
  - "tests/"                 # Skip test files
  - "migrations/"            # Skip migrations
  - "venv/"                  # Skip virtual environments
  - "__pycache__/"           # Skip cache
```

## 🎨 Examples

### Basic Python Project
```yaml
# Just add the workflow file above - works out of the box!
```

### Django Project
```yaml
# Add to your workflow before analysis:
- name: Django Setup
  run: |
    pip install django
    python manage.py collectstatic --noinput
```

### FastAPI Project
```yaml
# Add to your workflow before analysis:
- name: FastAPI Setup
  run: |
    pip install fastapi uvicorn
```

### Data Science Project
```yaml
# Add to your workflow before analysis:
- name: Data Science Setup
  run: |
    pip install jupyter pandas numpy matplotlib
```

## 📊 What You Get

### 1. Automated PR Comments
```markdown
## 🔍 Code Quality Report

**Overall Score**: 87/100 ✅

### 📊 Analysis Summary
- **Linting Issues**: 0 ✅
- **Type Coverage**: 85% ✅
- **Test Coverage**: 92% ✅
- **Documentation**: 78% ✅

### 🤖 AI Insights
- Consider adding type hints to `user_service.py`
- Function `process_data` could be optimized for better performance
- Add docstrings to public methods in `api/models.py`

### 🔒 Security
✅ No security issues found
```

### 2. Quality Badges
Add to your README:
```markdown
![Code Quality](https://img.shields.io/badge/Code%20Quality-87%2F100-brightgreen)
![Type Coverage](https://img.shields.io/badge/Type%20Coverage-85%25-green)
![Test Coverage](https://img.shields.io/badge/Test%20Coverage-92%25-brightgreen)
```

### 3. Detailed Reports
- JSON report with full analysis data
- Markdown summary for easy reading
- Downloadable artifacts with recommendations

## 🔧 Advanced Configuration

### Custom Analysis
```python
# .github/scripts/custom-analysis.py
def custom_quality_check(repo_path):
    # Your custom quality checks
    return {
        "custom_metric": 95,
        "recommendations": ["Custom suggestion"]
    }
```

### Integration with Existing CI
```yaml
# Add to existing workflow
- name: Quality Check
  uses: ./.github/workflows/python-quality.yml
```

### Slack/Teams Notifications
```yaml
- name: Notify Team
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: "Code quality check failed! 📊"
```

## 🎯 Benefits

✅ **Zero Maintenance**: Set it and forget it  
✅ **Instant Insights**: Get immediate feedback on code quality  
✅ **Team Alignment**: Consistent standards across all developers  
✅ **Learning Tool**: AI suggestions help improve coding skills  
✅ **Professional Standards**: Enterprise-grade code analysis  
✅ **Free to Use**: Open source and completely free  

## 🆘 Support

### Common Issues

**"Analysis failed"** → Check Python version (3.8+ required)  
**"MCP server timeout"** → Large repos may take longer, increase timeout  
**"Missing dependencies"** → Add your project's requirements to workflow  

### Getting Help

- 📖 [Full Documentation](https://github.com/your-org/python-mcp-server)
- 💬 [GitHub Discussions](https://github.com/your-org/python-mcp-server/discussions)
- 🐛 [Report Issues](https://github.com/your-org/python-mcp-server/issues)

## 🚀 What's Next?

- **Multi-language support** (JavaScript, TypeScript, Go)
- **Custom rule engines** for your specific requirements
- **Integration with more tools** (SonarQube, CodeClimate)
- **Performance benchmarking** and optimization suggestions

---

**Make your Python code shine! ✨**

*Add professional code quality to any repository in under 5 minutes.*
