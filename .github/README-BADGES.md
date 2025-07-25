# Code Quality Badges Template

Add these badges to your repository's README.md to showcase your Python code quality:

## Basic Quality Badges

```markdown
<!-- Replace 'your-username/your-repo' with your actual repository -->

![Code Quality](https://img.shields.io/badge/Code%20Quality-85%2F100-brightgreen)
![Type Coverage](https://img.shields.io/badge/Type%20Coverage-78%25-yellow)
![Test Coverage](https://img.shields.io/badge/Test%20Coverage-92%25-brightgreen)
![Lint Status](https://img.shields.io/badge/Lint-0%20issues-brightgreen)
![Documentation](https://img.shields.io/badge/Docs-85%25-brightgreen)
```

## GitHub Actions Status Badge

```markdown
[![Python Code Quality](https://github.com/your-username/your-repo/actions/workflows/python-quality.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/python-quality.yml)
```

## Dynamic Badges (Auto-updating)

If you set up the badge generation feature, use these dynamic badges:

```markdown
<!-- These update automatically with each analysis -->
![Quality Score](https://img.shields.io/endpoint?url=https://your-username.github.io/your-repo/quality-badge.json)
![Grade](https://img.shields.io/endpoint?url=https://your-username.github.io/your-repo/grade-badge.json)
```

## Complete Quality Section Template

Copy this section to your README.md:

```markdown
## 📊 Code Quality

[![Python Code Quality](https://github.com/your-username/your-repo/actions/workflows/python-quality.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/python-quality.yml)
![Code Quality](https://img.shields.io/badge/Code%20Quality-85%2F100-brightgreen)
![Type Coverage](https://img.shields.io/badge/Type%20Coverage-78%25-yellow)
![Test Coverage](https://img.shields.io/badge/Test%20Coverage-92%25-brightgreen)

This project maintains high code quality standards with automated analysis:

- **🐛 Linting**: Automated code style checking
- **🏷️ Type Safety**: Type annotation coverage tracking  
- **🧪 Testing**: Comprehensive test coverage analysis
- **📚 Documentation**: Docstring and documentation coverage
- **🔒 Security**: Automated security vulnerability scanning
- **🤖 AI Analysis**: AI-powered code quality insights

### Quality Reports

- [Latest Quality Report](https://github.com/your-username/your-repo/actions/workflows/python-quality.yml)
- [Detailed Analysis](https://your-username.github.io/your-repo/quality-report.html)

### Quick Local Test

Test code quality locally before committing:

```bash
# Download and run quick test
curl -s https://raw.githubusercontent.com/your-org/python-mcp-server/main/.github/scripts/quick-test.py | python3 - .
```
```

## Badge Color Guide

- **🟢 Green (brightgreen)**: Excellent (90-100%)
- **🟡 Yellow (yellow)**: Good (70-89%)  
- **🟠 Orange (orange)**: Fair (50-69%)
- **🔴 Red (red)**: Needs Improvement (0-49%)

## Customization

You can customize the badge appearance:

```markdown
<!-- Custom colors and labels -->
![Code Quality](https://img.shields.io/badge/Quality-A%2B-brightgreen?style=for-the-badge&logo=python)
![Tests](https://img.shields.io/badge/Tests-Passing-success?style=flat-square)
![Security](https://img.shields.io/badge/Security-Clean-blue?style=plastic)
```

## Advanced Features

### Quality Trend Chart

Add a quality trend chart to track improvements over time:

```markdown
## 📈 Quality Trend

![Quality Trend](https://your-username.github.io/your-repo/quality-trend.svg)
```

### Detailed Metrics Table

For more detailed quality information:

```markdown
## 📊 Detailed Metrics

| Metric | Score | Trend | Target |
|--------|-------|--------|--------|
| Overall Quality | 85/100 | 📈 +2 | 90+ |
| Linting | 0 issues | ✅ 0 | 0 |
| Type Coverage | 78% | 📈 +5% | 80%+ |
| Test Coverage | 92% | 📈 +3% | 90%+ |
| Documentation | 85% | 📊 = | 80%+ |
| Security | Clean | ✅ 0 | 0 issues |
| Complexity | Good | 📈 +1 | <10 avg |
```

## Integration Examples

### In Pull Request Template

Add to `.github/pull_request_template.md`:

```markdown
## Code Quality Checklist

- [ ] Code quality check passes (see CI status above)
- [ ] No new linting issues introduced
- [ ] Tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Security implications considered

**Quality Status**: Will be automatically reported by CI
```

### In Issue Templates

Add quality context to bug reports:

```markdown
**Code Quality Info**
Please run the quality check and include the score:
\`\`\`bash
curl -s https://raw.githubusercontent.com/your-org/python-mcp-server/main/.github/scripts/quick-test.py | python3 - .
\`\`\`
```

## Contributing Guidelines

Add to `CONTRIBUTING.md`:

```markdown
## Code Quality Standards

This project maintains high code quality standards. Before submitting:

1. **Run Local Quality Check**:
   ```bash
   python .github/scripts/quick-test.py .
   ```

2. **Fix Any Issues**:
   ```bash
   ruff --fix .          # Fix linting issues
   black .               # Format code
   pytest                # Run tests
   ```

3. **Ensure Quality Score ≥ 80**: Your changes should not decrease the overall quality score.

4. **Review CI Results**: All quality checks must pass before merge.
```

---

**Need help?** Check the [full setup guide](PYTHON_CODE_QUALITY_CICD.md) for detailed instructions.
