"""
Superior YAML/JSON processing and troubleshooting tools.

This module provides expert-level data format handling with advanced
validation, error detection, schema validation, and intelligent repair
capabilities that surpass any AI assistant.
"""

import json
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import difflib
import ast

try:
    import yaml
    from yaml.constructor import ConstructorError
    from yaml.parser import ParserError
    from yaml.scanner import ScannerError
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False

try:
    import ruamel.yaml
    from ruamel.yaml import YAML as RuamelYAML
    RUAMEL_AVAILABLE = True
except ImportError:
    ruamel = None
    RUAMEL_AVAILABLE = False

from ..utils.logging import log_tool_execution


class DataFormatAnalyzer:
    """Advanced data format analyzer with expert-level diagnostics."""
    
    def __init__(self):
        self.common_yaml_errors = self._load_yaml_error_patterns()
        self.common_json_errors = self._load_json_error_patterns()
        self.yaml_style_rules = self._load_yaml_style_rules()
        
    def _load_yaml_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common YAML error patterns and fixes."""
        return {
            "indentation_error": {
                "pattern": r"found character '\t'|mapping values are not allowed here",
                "description": "Indentation error - mixing tabs/spaces or incorrect indentation",
                "fix": "Use consistent spaces (2 or 4) for indentation, never tabs",
                "severity": "high"
            },
            "duplicate_keys": {
                "pattern": r"found duplicate key",
                "description": "Duplicate keys in YAML mapping",
                "fix": "Remove or rename duplicate keys",
                "severity": "critical"
            },
            "invalid_yaml_syntax": {
                "pattern": r"could not find expected|expected <block end>",
                "description": "Invalid YAML syntax structure",
                "fix": "Check for missing colons, incorrect nesting, or unclosed blocks",
                "severity": "high"
            },
            "scalar_format_error": {
                "pattern": r"could not determine a constructor for the tag",
                "description": "Invalid scalar value format",
                "fix": "Quote string values that might be interpreted as other types",
                "severity": "medium"
            },
            "anchor_reference_error": {
                "pattern": r"found undefined alias|found undefined anchor",
                "description": "Reference to undefined anchor",
                "fix": "Define anchor before referencing or fix anchor name",
                "severity": "high"
            }
        }
    
    def _load_json_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common JSON error patterns and fixes."""
        return {
            "trailing_comma": {
                "pattern": r"Expecting property name|Expecting value",
                "description": "Trailing comma in JSON (not allowed)",
                "fix": "Remove trailing commas after last array/object elements",
                "severity": "high"
            },
            "unquoted_keys": {
                "pattern": r"Expecting property name enclosed in double quotes",
                "description": "Unquoted object keys",
                "fix": "Wrap all object keys in double quotes",
                "severity": "high"
            },
            "single_quotes": {
                "pattern": r"Expecting value|Invalid control character",
                "description": "Single quotes used instead of double quotes",
                "fix": "Use double quotes for all strings in JSON",
                "severity": "high"
            },
            "missing_quotes": {
                "pattern": r"Expecting value",
                "description": "Missing quotes around string values",
                "fix": "Wrap string values in double quotes",
                "severity": "high"
            },
            "invalid_escape": {
                "pattern": r"Invalid \\escape|Invalid control character",
                "description": "Invalid escape sequence",
                "fix": "Use proper JSON escape sequences (\\n, \\t, \\\", \\\\)",
                "severity": "medium"
            }
        }
    
    def _load_yaml_style_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load YAML style best practices."""
        return {
            "consistent_indentation": {
                "description": "Use consistent indentation (2 or 4 spaces)",
                "check": lambda content: self._check_consistent_indentation(content),
                "severity": "medium"
            },
            "no_tabs": {
                "description": "Never use tabs for indentation",
                "check": lambda content: '\t' not in content,
                "severity": "high"
            },
            "trailing_spaces": {
                "description": "Avoid trailing whitespace",
                "check": lambda content: not any(line.rstrip() != line for line in content.split('\n')),
                "severity": "low"
            },
            "document_separators": {
                "description": "Use --- for document separators",
                "check": lambda content: self._check_document_separators(content),
                "severity": "low"
            },
            "boolean_lowercase": {
                "description": "Use lowercase for boolean values (true/false)",
                "check": lambda content: not re.search(r'\b(True|False|TRUE|FALSE)\b', content),
                "severity": "medium"
            }
        }
    
    def _check_consistent_indentation(self, content: str) -> bool:
        """Check if YAML uses consistent indentation."""
        lines = content.split('\n')
        indentations = set()
        
        for line in lines:
            if line.strip() and line.startswith(' '):
                # Count leading spaces
                spaces = len(line) - len(line.lstrip(' '))
                if spaces > 0:
                    indentations.add(spaces)
        
        # Check if all indentations are multiples of the smallest
        if not indentations:
            return True
        
        min_indent = min(indentations)
        return all(indent % min_indent == 0 for indent in indentations)
    
    def _check_document_separators(self, content: str) -> bool:
        """Check proper use of YAML document separators."""
        lines = content.split('\n')
        has_multiple_docs = content.count('---') > 1
        
        if has_multiple_docs:
            # Check that separators are on their own lines
            for i, line in enumerate(lines):
                if '---' in line and line.strip() != '---':
                    return False
        
        return True


class YAMLProcessor:
    """Advanced YAML processing with expert-level error handling."""
    
    def __init__(self):
        self.analyzer = DataFormatAnalyzer()
        
    def validate_yaml(self, content: str) -> Dict[str, Any]:
        """Comprehensive YAML validation and analysis."""
        if not YAML_AVAILABLE:
            return {"error": "PyYAML not available", "valid": False}
        
        result = {
            "valid": False,
            "data": None,
            "errors": [],
            "warnings": [],
            "style_issues": [],
            "suggestions": [],
            "metadata": {}
        }
        
        # Basic syntax validation
        try:
            data = yaml.safe_load(content)
            result["valid"] = True
            result["data"] = data
            result["metadata"]["type"] = type(data).__name__
            
            if isinstance(data, dict):
                result["metadata"]["keys"] = list(data.keys())
                result["metadata"]["depth"] = self._calculate_dict_depth(data)
            elif isinstance(data, list):
                result["metadata"]["length"] = len(data)
                result["metadata"]["types"] = list(set(type(item).__name__ for item in data))
        
        except (ParserError, ScannerError, ConstructorError) as e:
            line_num = None
            column_num = None

            if hasattr(e, 'problem_mark') and e.problem_mark:
                line_num = e.problem_mark.line + 1
                column_num = e.problem_mark.column + 1

            error_msg = str(e)
            fix_suggestion = self._suggest_yaml_fix(error_msg)
            
            result["errors"].append({
                "type": "syntax_error",
                "message": error_msg,
                "line": line_num,
                "column": column_num,
                "severity": "critical",
                "fix_suggestion": fix_suggestion
            })
            
            # Add to suggestions if we have a fix
            if fix_suggestion and fix_suggestion != "Check YAML syntax and formatting":
                result["suggestions"].append({
                    "type": "syntax_fix",
                    "description": fix_suggestion,
                    "line": line_num,
                    "column": column_num
                })
        except Exception as e:
            result["errors"].append({
                "type": "unknown_error",
                "message": str(e),
                "severity": "critical"
            })
        
        # Style analysis
        style_issues = self._analyze_yaml_style(content)
        result["style_issues"] = style_issues
        
        # Security analysis
        security_issues = self._analyze_yaml_security(content)
        result["warnings"].extend(security_issues)
        
        # Best practices suggestions
        suggestions = self._generate_yaml_suggestions(content, result["data"])
        result["suggestions"] = suggestions
        
        return result
    
    def _suggest_yaml_fix(self, error_message: str) -> str:
        """Suggest fixes for common YAML errors."""
        for error_type, pattern_info in self.analyzer.common_yaml_errors.items():
            if re.search(pattern_info["pattern"], error_message, re.IGNORECASE):
                return pattern_info["fix"]
        
        return "Check YAML syntax and structure"
    
    def _analyze_yaml_style(self, content: str) -> List[Dict[str, Any]]:
        """Analyze YAML style and formatting."""
        issues = []
        
        for rule_name, rule_info in self.analyzer.yaml_style_rules.items():
            try:
                if not rule_info["check"](content):
                    issues.append({
                        "rule": rule_name,
                        "description": rule_info["description"],
                        "severity": rule_info["severity"],
                        "type": "style"
                    })
            except Exception:
                pass  # Skip rules that fail
        
        # Additional specific checks
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for tabs
            if '\t' in line:
                issues.append({
                    "rule": "no_tabs",
                    "description": f"Line {i}: Tab character found (use spaces)",
                    "line": i,
                    "severity": "high",
                    "type": "style"
                })
            
            # Check for trailing spaces
            if line.endswith(' '):
                issues.append({
                    "rule": "trailing_spaces",
                    "description": f"Line {i}: Trailing whitespace",
                    "line": i,
                    "severity": "low",
                    "type": "style"
                })
        
        return issues
    
    def _analyze_yaml_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze YAML for potential security issues."""
        warnings = []
        
        # Check for dangerous constructors
        dangerous_patterns = [
            (r'!!python/', "Dangerous Python object constructor"),
            (r'!!java/', "Dangerous Java object constructor"),
            (r'!!ruby/', "Dangerous Ruby object constructor"),
            (r'!!perl/', "Dangerous Perl object constructor"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content):
                warnings.append({
                    "type": "security",
                    "description": description,
                    "severity": "critical",
                    "recommendation": "Use safe_load() and avoid custom constructors"
                })
        
        # Check for suspicious values
        suspicious_patterns = [
            (r'password\s*:\s*[^\s]+', "Hardcoded password detected"),
            (r'secret\s*:\s*[^\s]+', "Hardcoded secret detected"),
            (r'api[_-]?key\s*:\s*[^\s]+', "Hardcoded API key detected"),
            (r'token\s*:\s*[^\s]+', "Hardcoded token detected"),
        ]
        
        for pattern, description in suspicious_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                warnings.append({
                    "type": "security",
                    "description": description,
                    "line": line_num,
                    "severity": "high",
                    "recommendation": "Use environment variables or secure secret management"
                })
        
        return warnings
    
    def _generate_yaml_suggestions(self, content: str, data: Any) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for YAML."""
        suggestions = []
        
        # Check for improvements
        if isinstance(data, dict):
            # Suggest schema validation
            suggestions.append({
                "type": "enhancement",
                "description": "Consider adding schema validation",
                "benefit": "Ensure data consistency and catch errors early",
                "example": "Use JSON Schema or custom validation"
            })
            
            # Check for missing documentation
            if len(data) > 5 and not any(key.startswith('#') for key in str(content)):
                suggestions.append({
                    "type": "documentation",
                    "description": "Add comments to document complex sections",
                    "benefit": "Improve maintainability and understanding"
                })
        
        # Check for environment variable usage
        env_vars = re.findall(r'\$\{([^}]+)\}', content)
        if env_vars:
            suggestions.append({
                "type": "environment",
                "description": f"Environment variables detected: {', '.join(set(env_vars))}",
                "benefit": "Good practice for configuration management",
                "note": "Ensure all variables are documented and have defaults"
            })
        
        return suggestions
    
    def _calculate_dict_depth(self, d: Dict) -> int:
        """Calculate maximum depth of nested dictionary."""
        if not isinstance(d, dict) or not d:
            return 0
        
        return 1 + max(self._calculate_dict_depth(v) if isinstance(v, dict) else 0 for v in d.values())
    
    def repair_yaml(self, content: str) -> Dict[str, Any]:
        """Attempt to repair common YAML issues."""
        if not YAML_AVAILABLE:
            return {"error": "PyYAML not available", "repaired": False}
        
        original_content = content
        repaired_content = content
        repairs_made = []
        
        try:
            # Try to load first to see if it's already valid
            yaml.safe_load(content)
            return {
                "repaired": False,
                "original_valid": True,
                "content": content,
                "message": "YAML is already valid"
            }
        except Exception:
            pass  # Continue with repairs
        
        # Fix common issues
        
        # 1. Replace tabs with spaces
        if '\t' in repaired_content:
            repaired_content = repaired_content.replace('\t', '  ')
            repairs_made.append("Replaced tabs with spaces")
        
        # 2. Fix trailing commas (YAML doesn't need them)
        repaired_content = re.sub(r',(\s*\n\s*[}\]])', r'\1', repaired_content)
        if repaired_content != content:
            repairs_made.append("Removed trailing commas")
        
        # 3. Fix common boolean values
        boolean_fixes = {
            r'\bTrue\b': 'true',
            r'\bFalse\b': 'false',
            r'\bTRUE\b': 'true',
            r'\bFALSE\b': 'false',
            r'\bNone\b': 'null',
            r'\bNULL\b': 'null'
        }
        
        for pattern, replacement in boolean_fixes.items():
            old_content = repaired_content
            repaired_content = re.sub(pattern, replacement, repaired_content)
            if repaired_content != old_content:
                repairs_made.append(f"Fixed boolean/null values: {pattern} -> {replacement}")
        
        # 4. Try to fix indentation issues
        repaired_content = self._fix_yaml_indentation(repaired_content)
        if repaired_content != content:
            repairs_made.append("Fixed indentation issues")
        
        # 5. Quote problematic values
        repaired_content = self._quote_problematic_values(repaired_content)
        
        # Test if repairs worked
        try:
            yaml.safe_load(repaired_content)
            return {
                "repaired": True,
                "original_valid": False,
                "content": repaired_content,
                "repairs_made": repairs_made,
                "diff": self._generate_diff(original_content, repaired_content)
            }
        except Exception as e:
            return {
                "repaired": False,
                "original_valid": False,
                "content": repaired_content,
                "repairs_attempted": repairs_made,
                "final_error": str(e),
                "diff": self._generate_diff(original_content, repaired_content)
            }
    
    def _fix_yaml_indentation(self, content: str) -> str:
        """Attempt to fix YAML indentation issues."""
        lines = content.split('\n')
        fixed_lines = []
        current_indent = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Detect list items
            if stripped.startswith('- '):
                # Keep current indentation level for list items
                fixed_lines.append(' ' * current_indent + stripped)
            elif ':' in stripped and not stripped.endswith(':'):
                # Key-value pair
                if current_indent == 0:
                    fixed_lines.append(stripped)
                else:
                    fixed_lines.append(' ' * current_indent + stripped)
            elif stripped.endswith(':'):
                # Key only - might need to increase indent for next items
                if current_indent == 0:
                    fixed_lines.append(stripped)
                else:
                    fixed_lines.append(' ' * current_indent + stripped)
                current_indent += 2
            else:
                # Regular content
                fixed_lines.append(' ' * current_indent + stripped)
        
        return '\n'.join(fixed_lines)
    
    def _quote_problematic_values(self, content: str) -> str:
        """Quote values that might cause parsing issues."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    value = value.strip()
                    
                    # Quote values that start with special characters
                    if value and not value.startswith(('"', "'", '[', '{')) and any(char in value for char in ['@', '%', '&', '*', '!', '|', '>', '<']):
                        line = f"{key}: \"{value}\""
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _generate_diff(self, original: str, repaired: str) -> List[str]:
        """Generate diff between original and repaired content."""
        return list(difflib.unified_diff(
            original.splitlines(keepends=True),
            repaired.splitlines(keepends=True),
            fromfile="original.yaml",
            tofile="repaired.yaml",
            lineterm=""
        ))


class JSONProcessor:
    """Advanced JSON processing with expert-level error handling."""
    
    def __init__(self):
        self.analyzer = DataFormatAnalyzer()
    
    def validate_json(self, content: str) -> Dict[str, Any]:
        """Comprehensive JSON validation and analysis."""
        result = {
            "valid": False,
            "data": None,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metadata": {}
        }
        
        # Basic syntax validation
        try:
            data = json.loads(content)
            result["valid"] = True
            result["data"] = data
            result["metadata"]["type"] = type(data).__name__
            result["metadata"]["size_bytes"] = len(content)
            
            if isinstance(data, dict):
                result["metadata"]["keys"] = list(data.keys())
                result["metadata"]["depth"] = self._calculate_dict_depth(data)
                result["metadata"]["key_count"] = len(data)
            elif isinstance(data, list):
                result["metadata"]["length"] = len(data)
                result["metadata"]["types"] = list(set(type(item).__name__ for item in data))
            
        except json.JSONDecodeError as e:
            result["errors"].append({
                "type": "syntax_error",
                "message": str(e),
                "line": e.lineno if hasattr(e, 'lineno') else None,
                "column": e.colno if hasattr(e, 'colno') else None,
                "position": e.pos if hasattr(e, 'pos') else None,
                "severity": "critical",
                "fix_suggestion": self._suggest_json_fix(str(e), content, getattr(e, 'pos', 0))
            })
        except Exception as e:
            result["errors"].append({
                "type": "unknown_error",
                "message": str(e),
                "severity": "critical"
            })
        
        # Style analysis
        style_issues = self._analyze_json_style(content)
        result["warnings"].extend(style_issues)
        
        # Security analysis
        security_issues = self._analyze_json_security(content)
        result["warnings"].extend(security_issues)
        
        # Performance suggestions
        performance_suggestions = self._generate_json_performance_suggestions(content, result.get("data"))
        result["suggestions"].extend(performance_suggestions)
        
        return result
    
    def _suggest_json_fix(self, error_message: str, content: str, position: int) -> str:
        """Suggest fixes for common JSON errors with context."""
        # Get context around error position
        lines = content.split('\n')
        char_count = 0
        error_line = 0
        error_col = 0
        
        for i, line in enumerate(lines):
            if char_count + len(line) >= position:
                error_line = i + 1
                error_col = position - char_count
                break
            char_count += len(line) + 1  # +1 for newline
        
        # Analyze the error context
        if error_line > 0 and error_line <= len(lines):
            context_line = lines[error_line - 1]
            
            # Check for specific error patterns
            for error_type, pattern_info in self.analyzer.common_json_errors.items():
                if re.search(pattern_info["pattern"], error_message, re.IGNORECASE):
                    # Provide context-specific suggestions
                    if error_type == "trailing_comma":
                        if context_line.rstrip().endswith(','):
                            return f"Remove trailing comma on line {error_line}: '{context_line.strip()}'"
                    elif error_type == "single_quotes":
                        return f"Replace single quotes with double quotes on line {error_line}"
                    
                    return pattern_info["fix"]
        
        return "Check JSON syntax near the error position"
    
    def _analyze_json_style(self, content: str) -> List[Dict[str, Any]]:
        """Analyze JSON style and formatting."""
        issues = []
        
        # Check for consistent indentation
        lines = content.split('\n')
        indentations = []
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indentations.append(leading_spaces)
                
                # Check for tabs
                if '\t' in line:
                    issues.append({
                        "type": "style",
                        "description": f"Line {i}: Tab character found (use spaces)",
                        "line": i,
                        "severity": "medium"
                    })
        
        # Check indentation consistency
        if indentations:
            unique_indents = set(indentations)
            if len(unique_indents) > 1:
                min_indent = min(unique_indents)
                if not all(indent % min_indent == 0 for indent in unique_indents):
                    issues.append({
                        "type": "style",
                        "description": "Inconsistent indentation detected",
                        "severity": "medium",
                        "suggestion": f"Use consistent indentation (recommend {min_indent} spaces)"
                    })
        
        # Check for minified vs. formatted
        if '\n' not in content.strip():
            issues.append({
                "type": "style",
                "description": "JSON is minified (single line)",
                "severity": "low",
                "suggestion": "Consider formatting for better readability"
            })
        
        return issues
    
    def _analyze_json_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze JSON for potential security issues."""
        warnings = []
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r'"password"\s*:\s*"[^"]*"', "Hardcoded password detected"),
            (r'"secret"\s*:\s*"[^"]*"', "Hardcoded secret detected"),
            (r'"api[_-]?key"\s*:\s*"[^"]*"', "Hardcoded API key detected"),
            (r'"token"\s*:\s*"[^"]*"', "Hardcoded token detected"),
            (r'"private[_-]?key"\s*:\s*"[^"]*"', "Private key detected"),
        ]
        
        for pattern, description in suspicious_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                warnings.append({
                    "type": "security",
                    "description": description,
                    "line": line_num,
                    "severity": "high",
                    "recommendation": "Use environment variables or secure secret management"
                })
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            (r'"eval"\s*:', "Eval function reference"),
            (r'"exec"\s*:', "Exec function reference"),
            (r'"script"\s*:\s*"[^"]*<script', "Potential XSS payload"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append({
                    "type": "security",
                    "description": description,
                    "severity": "critical",
                    "recommendation": "Review and sanitize dangerous content"
                })
        
        return warnings
    
    def _generate_json_performance_suggestions(self, content: str, data: Any) -> List[Dict[str, Any]]:
        """Generate performance optimization suggestions."""
        suggestions = []
        
        if data is None:
            return suggestions
        
        # Size analysis
        size_bytes = len(content)
        if size_bytes > 1024 * 1024:  # > 1MB
            suggestions.append({
                "type": "performance",
                "description": f"Large JSON file ({size_bytes / 1024 / 1024:.1f}MB)",
                "recommendation": "Consider pagination, compression, or streaming",
                "severity": "medium"
            })
        
        # Depth analysis
        if isinstance(data, (dict, list)):
            depth = self._calculate_dict_depth(data)
            if depth > 10:
                suggestions.append({
                    "type": "performance",
                    "description": f"Deep nesting detected (depth: {depth})",
                    "recommendation": "Consider flattening structure for better performance",
                    "severity": "low"
                })
        
        # Array size analysis
        if isinstance(data, list) and len(data) > 10000:
            suggestions.append({
                "type": "performance",
                "description": f"Large array ({len(data)} items)",
                "recommendation": "Consider pagination or chunking for large datasets",
                "severity": "medium"
            })
        
        # String key analysis
        if isinstance(data, dict):
            long_keys = [k for k in data.keys() if isinstance(k, str) and len(k) > 50]
            if long_keys:
                suggestions.append({
                    "type": "performance",
                    "description": f"Long key names detected: {len(long_keys)} keys",
                    "recommendation": "Consider shorter, more concise key names",
                    "severity": "low"
                })
        
        return suggestions
    
    def _calculate_dict_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested structure."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_dict_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_dict_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def repair_json(self, content: str) -> Dict[str, Any]:
        """Attempt to repair common JSON issues."""
        original_content = content
        repaired_content = content
        repairs_made = []
        
        try:
            # Try to load first to see if it's already valid
            json.loads(content)
            return {
                "repaired": False,
                "original_valid": True,
                "content": content,
                "message": "JSON is already valid"
            }
        except Exception:
            pass  # Continue with repairs
        
        # Common repairs
        
        # 1. Remove trailing commas
        repaired_content = re.sub(r',(\s*[}\]])', r'\1', repaired_content)
        if repaired_content != content:
            repairs_made.append("Removed trailing commas")
        
        # 2. Fix single quotes to double quotes
        # Be careful not to break escaped quotes
        repaired_content = re.sub(r"'([^'\\]*(\\.[^'\\]*)*)'", r'"\1"', repaired_content)
        if repaired_content != original_content:
            repairs_made.append("Fixed single quotes to double quotes")
        
        # 3. Quote unquoted keys
        repaired_content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', repaired_content)
        if repaired_content != original_content:
            repairs_made.append("Added quotes to unquoted keys")
        
        # 4. Fix Python boolean/None values
        boolean_fixes = {
            r'\bTrue\b': 'true',
            r'\bFalse\b': 'false',
            r'\bNone\b': 'null'
        }
        
        for pattern, replacement in boolean_fixes.items():
            old_content = repaired_content
            repaired_content = re.sub(pattern, replacement, repaired_content)
            if repaired_content != old_content:
                repairs_made.append(f"Fixed Python values: {pattern} -> {replacement}")
        
        # 5. Try to fix missing quotes on string values
        repaired_content = self._fix_unquoted_strings(repaired_content)
        if repaired_content != original_content:
            repairs_made.append("Added quotes to unquoted string values")
        
        # Test if repairs worked
        try:
            json.loads(repaired_content)
            return {
                "repaired": True,
                "original_valid": False,
                "content": repaired_content,
                "repairs_made": repairs_made,
                "diff": self._generate_diff(original_content, repaired_content)
            }
        except Exception as e:
            return {
                "repaired": False,
                "original_valid": False,
                "content": repaired_content,
                "repairs_attempted": repairs_made,
                "final_error": str(e),
                "diff": self._generate_diff(original_content, repaired_content)
            }
    
    def _fix_unquoted_strings(self, content: str) -> str:
        """Attempt to fix unquoted string values."""
        # This is tricky - we need to identify string values that should be quoted
        # but aren't, without breaking valid JSON
        
        # Look for patterns like: "key": value where value should be quoted
        pattern = r'("[\w\s]+"\s*:\s*)([a-zA-Z][a-zA-Z0-9\s]*[a-zA-Z0-9])(?=\s*[,}\]])' 
        
        def quote_replacement(match):
            key_part = match.group(1)
            value_part = match.group(2)
            
            # Don't quote if it's already a valid JSON value
            if value_part.lower() in ['true', 'false', 'null'] or value_part.isdigit():
                return match.group(0)
            
            return f'{key_part}"{value_part}"'
        
        return re.sub(pattern, quote_replacement, content)
    
    def _generate_diff(self, original: str, repaired: str) -> List[str]:
        """Generate diff between original and repaired content."""
        return list(difflib.unified_diff(
            original.splitlines(keepends=True),
            repaired.splitlines(keepends=True),
            fromfile="original.json",
            tofile="repaired.json",
            lineterm=""
        ))


class SchemaValidator:
    """Advanced schema validation for JSON/YAML data."""
    
    def __init__(self):
        self.built_in_schemas = self._load_built_in_schemas()
    
    def _load_built_in_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load common schema patterns."""
        return {
            "docker-compose": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "services": {"type": "object"},
                    "volumes": {"type": "object"},
                    "networks": {"type": "object"}
                },
                "required": ["version", "services"]
            },
            "package.json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "main": {"type": "string"},
                    "scripts": {"type": "object"},
                    "dependencies": {"type": "object"},
                    "devDependencies": {"type": "object"}
                },
                "required": ["name", "version"]
            },
            "kubernetes": {
                "type": "object",
                "properties": {
                    "apiVersion": {"type": "string"},
                    "kind": {"type": "string"},
                    "metadata": {"type": "object"},
                    "spec": {"type": "object"}
                },
                "required": ["apiVersion", "kind", "metadata"]
            }
        }
    
    def validate_with_schema(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against JSON schema."""
        if not JSONSCHEMA_AVAILABLE:
            return {"error": "jsonschema not available", "valid": False}
        
        result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            validate(instance=data, schema=schema)
            result["valid"] = True
        except ValidationError as e:
            result["errors"].append({
                "message": e.message,
                "path": list(e.absolute_path),
                "validator": e.validator,
                "validator_value": e.validator_value,
                "schema_path": list(e.schema_path)
            })
        except Exception as e:
            result["errors"].append({
                "message": str(e),
                "type": "schema_error"
            })
        
        return result
    
    def detect_schema_type(self, data: Any) -> Optional[str]:
        """Attempt to detect the type of schema/format."""
        if not isinstance(data, dict):
            return None
        
        # Check for common patterns
        if "version" in data and "services" in data:
            return "docker-compose"
        
        if "name" in data and "version" in data and ("dependencies" in data or "scripts" in data):
            return "package.json"
        
        if "apiVersion" in data and "kind" in data and "metadata" in data:
            return "kubernetes"
        
        if "swagger" in data or "openapi" in data:
            return "openapi"
        
        return None


# Main tool functions
@log_tool_execution("validate_yaml")
def validate_yaml(content: str) -> Dict[str, Any]:
    """
    Comprehensive YAML validation with expert-level error detection and repair suggestions.
    
    Args:
        content: YAML content to validate
        
    Returns:
        Dict with validation results, errors, warnings, style issues, and suggestions
    """
    processor = YAMLProcessor()
    return processor.validate_yaml(content)


@log_tool_execution("validate_json")  
def validate_json(content: str) -> Dict[str, Any]:
    """
    Comprehensive JSON validation with expert-level error detection and optimization suggestions.
    
    Args:
        content: JSON content to validate
        
    Returns:
        Dict with validation results, errors, warnings, and performance suggestions
    """
    processor = JSONProcessor()
    return processor.validate_json(content)


@log_tool_execution("repair_yaml")
def repair_yaml(content: str) -> Dict[str, Any]:
    """
    Automatically repair common YAML syntax and formatting issues.
    
    Args:
        content: Broken YAML content to repair
        
    Returns:
        Dict with repair results, fixed content, and diff showing changes
    """
    processor = YAMLProcessor()
    return processor.repair_yaml(content)


@log_tool_execution("repair_json")
def repair_json(content: str) -> Dict[str, Any]:
    """
    Automatically repair common JSON syntax issues.
    
    Args:
        content: Broken JSON content to repair
        
    Returns:
        Dict with repair results, fixed content, and diff showing changes
    """
    processor = JSONProcessor()
    return processor.repair_json(content)


@log_tool_execution("format_yaml")
def format_yaml(content: str, indent: int = 2, width: int = 80) -> Dict[str, Any]:
    """
    Format YAML with consistent style and best practices.
    
    Args:
        content: YAML content to format
        indent: Number of spaces for indentation
        width: Maximum line width
        
    Returns:
        Dict with formatted content and formatting changes
    """
    if not RUAMEL_AVAILABLE:
        return {"error": "ruamel.yaml not available for formatting", "formatted": False}
    
    try:
        yaml_formatter = RuamelYAML()
        yaml_formatter.preserve_quotes = True
        yaml_formatter.map_indent = indent
        yaml_formatter.sequence_indent = indent
        yaml_formatter.width = width
        
        # Load and dump to format
        data = yaml_formatter.load(content)
        
        from io import StringIO
        output = StringIO()
        yaml_formatter.dump(data, output)
        formatted_content = output.getvalue()
        
        return {
            "formatted": True,
            "content": formatted_content,
            "changes": content != formatted_content,
            "settings": {
                "indent": indent,
                "width": width
            }
        }
        
    except Exception as e:
        return {
            "formatted": False,
            "error": str(e),
            "original_content": content
        }


@log_tool_execution("format_json")
def format_json(content: str, indent: int = 2, sort_keys: bool = False) -> Dict[str, Any]:
    """
    Format JSON with consistent style and indentation.
    
    Args:
        content: JSON content to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort object keys
        
    Returns:
        Dict with formatted content and formatting changes
    """
    try:
        data = json.loads(content)
        formatted_content = json.dumps(
            data, 
            indent=indent, 
            sort_keys=sort_keys,
            ensure_ascii=False,
            separators=(',', ': ')
        )
        
        return {
            "formatted": True,
            "content": formatted_content,
            "changes": content != formatted_content,
            "settings": {
                "indent": indent,
                "sort_keys": sort_keys
            }
        }
        
    except Exception as e:
        return {
            "formatted": False,
            "error": str(e),
            "original_content": content
        }


@log_tool_execution("convert_yaml_to_json")
def convert_yaml_to_json(yaml_content: str, indent: int = 2) -> Dict[str, Any]:
    """
    Convert YAML to JSON format.
    
    Args:
        yaml_content: YAML content to convert
        indent: JSON indentation
        
    Returns:
        Dict with converted JSON content
    """
    if not YAML_AVAILABLE:
        return {"error": "PyYAML not available", "converted": False}
    
    try:
        data = yaml.safe_load(yaml_content)
        json_content = json.dumps(data, indent=indent, ensure_ascii=False)
        
        return {
            "converted": True,
            "json_content": json_content,
            "yaml_content": yaml_content
        }
        
    except Exception as e:
        return {
            "converted": False,
            "error": str(e),
            "yaml_content": yaml_content
        }


@log_tool_execution("convert_json_to_yaml")
def convert_json_to_yaml(json_content: str, indent: int = 2) -> Dict[str, Any]:
    """
    Convert JSON to YAML format.
    
    Args:
        json_content: JSON content to convert
        indent: YAML indentation
        
    Returns:
        Dict with converted YAML content
    """
    if not YAML_AVAILABLE:
        return {"error": "PyYAML not available", "converted": False}
    
    try:
        data = json.loads(json_content)
        yaml_content = yaml.dump(
            data, 
            default_flow_style=False, 
            indent=indent,
            allow_unicode=True
        )
        
        return {
            "converted": True,
            "yaml_content": yaml_content,
            "json_content": json_content
        }
        
    except Exception as e:
        return {
            "converted": False,
            "error": str(e),
            "json_content": json_content
        }


@log_tool_execution("validate_with_schema")
def validate_with_schema(data_content: str, schema_content: str, data_format: str = "json") -> Dict[str, Any]:
    """
    Validate JSON/YAML data against a JSON schema.
    
    Args:
        data_content: Data to validate (JSON or YAML)
        schema_content: JSON schema for validation
        data_format: Format of data ("json" or "yaml")
        
    Returns:
        Dict with validation results and detailed error information
    """
    if not JSONSCHEMA_AVAILABLE:
        return {"error": "jsonschema not available", "valid": False}
    
    try:
        # Parse schema
        schema = json.loads(schema_content)
        
        # Parse data based on format
        if data_format.lower() == "yaml":
            if not YAML_AVAILABLE:
                return {"error": "PyYAML not available for YAML parsing", "valid": False}
            data = yaml.safe_load(data_content)
        else:
            data = json.loads(data_content)
        
        # Validate
        validator = SchemaValidator()
        return validator.validate_with_schema(data, schema)
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "data_format": data_format
        }


@log_tool_execution("detect_format")
def detect_format(content: str) -> Dict[str, Any]:
    """
    Detect whether content is JSON, YAML, or other format and provide analysis.
    
    Args:
        content: Content to analyze
        
    Returns:
        Dict with format detection results and confidence scores
    """
    result = {
        "detected_format": None,
        "confidence": 0.0,
        "analysis": {},
        "suggestions": []
    }
    
    # Clean content for analysis
    clean_content = content.strip()
    
    if not clean_content:
        result["detected_format"] = "empty"
        return result
    
    # JSON detection
    json_score = 0
    yaml_score = 0
    
    # JSON indicators
    if clean_content.startswith(('{', '[')):
        json_score += 30
    if clean_content.endswith(('}', ']')):
        json_score += 30
    if '"' in clean_content and ':' in clean_content:
        json_score += 20
    if clean_content.count('"') % 2 == 0:  # Paired quotes
        json_score += 10
    
    # YAML indicators  
    if ':' in clean_content and not clean_content.startswith(('{', '[')):
        yaml_score += 25
    if '\n' in clean_content and not clean_content.startswith(('{', '[')):
        yaml_score += 20
    if re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:', clean_content, re.MULTILINE):
        yaml_score += 25
    if '- ' in clean_content:  # YAML list indicator
        yaml_score += 15
    
    # Test actual parsing
    try:
        json.loads(clean_content)
        json_score += 50
        result["analysis"]["json_parseable"] = True
    except:
        result["analysis"]["json_parseable"] = False
    
    if YAML_AVAILABLE:
        try:
            yaml.safe_load(clean_content)
            yaml_score += 30
            result["analysis"]["yaml_parseable"] = True
        except:
            result["analysis"]["yaml_parseable"] = False
    
    # Determine format
    if json_score > yaml_score:
        result["detected_format"] = "json"
        result["confidence"] = min(json_score / 100.0, 1.0)
    elif yaml_score > 0:
        result["detected_format"] = "yaml"
        result["confidence"] = min(yaml_score / 100.0, 1.0)
    else:
        result["detected_format"] = "unknown"
        result["confidence"] = 0.0
    
    # Add analysis details
    result["analysis"]["json_score"] = json_score
    result["analysis"]["yaml_score"] = yaml_score
    result["analysis"]["line_count"] = len(clean_content.split('\n'))
    result["analysis"]["char_count"] = len(clean_content)
    
    # Suggestions based on analysis
    if result["detected_format"] == "unknown":
        result["suggestions"].append("Content format unclear - try validating as JSON or YAML")
    elif result["confidence"] < 0.7:
        result["suggestions"].append(f"Low confidence detection - verify {result['detected_format']} format")
    
    return result


@log_tool_execution("compare_data_structures")
def compare_data_structures(content1: str, content2: str, format1: str = "auto", format2: str = "auto") -> Dict[str, Any]:
    """
    Compare two data structures (JSON/YAML) and highlight differences.
    
    Args:
        content1: First data structure content
        content2: Second data structure content  
        format1: Format of first content ("json", "yaml", or "auto")
        format2: Format of second content ("json", "yaml", or "auto")
        
    Returns:
        Dict with comparison results, differences, and analysis
    """
    result = {
        "equal": False,
        "differences": [],
        "analysis": {},
        "errors": []
    }
    
    try:
        # Auto-detect formats if needed
        if format1 == "auto":
            detection = detect_format(content1)
            format1 = detection["detected_format"]
        
        if format2 == "auto":
            detection = detect_format(content2)
            format2 = detection["detected_format"]
        
        # Parse data structures
        def parse_content(content, fmt):
            if fmt == "json":
                return json.loads(content)
            elif fmt == "yaml":
                if not YAML_AVAILABLE:
                    raise Exception("PyYAML not available")
                return yaml.safe_load(content)
            else:
                raise Exception(f"Unsupported format: {fmt}")
        
        data1 = parse_content(content1, format1)
        data2 = parse_content(content2, format2)
        
        # Compare structures
        result["equal"] = data1 == data2
        result["analysis"]["format1"] = format1
        result["analysis"]["format2"] = format2
        result["analysis"]["type1"] = type(data1).__name__
        result["analysis"]["type2"] = type(data2).__name__
        
        if not result["equal"]:
            # Find differences
            differences = _find_differences(data1, data2, path=[])
            result["differences"] = differences
        
        # Additional analysis
        if isinstance(data1, dict) and isinstance(data2, dict):
            keys1 = set(data1.keys())
            keys2 = set(data2.keys())
            
            result["analysis"]["keys_only_in_1"] = list(keys1 - keys2)
            result["analysis"]["keys_only_in_2"] = list(keys2 - keys1)
            result["analysis"]["common_keys"] = list(keys1 & keys2)
        
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def _find_differences(obj1: Any, obj2: Any, path: List[str] = None) -> List[Dict[str, Any]]:
    """Recursively find differences between two objects."""
    if path is None:
        path = []
    
    differences = []
    
    if type(obj1) != type(obj2):
        differences.append({
            "path": ".".join(path) if path else "root",
            "type": "type_mismatch",
            "value1": {"type": type(obj1).__name__, "value": obj1},
            "value2": {"type": type(obj2).__name__, "value": obj2}
        })
        return differences
    
    if isinstance(obj1, dict):
        keys1 = set(obj1.keys())
        keys2 = set(obj2.keys())
        
        # Keys only in obj1
        for key in keys1 - keys2:
            differences.append({
                "path": ".".join(path + [str(key)]) if path else str(key),
                "type": "key_added",
                "value1": obj1[key],
                "value2": None
            })
        
        # Keys only in obj2
        for key in keys2 - keys1:
            differences.append({
                "path": ".".join(path + [str(key)]) if path else str(key),
                "type": "key_removed", 
                "value1": None,
                "value2": obj2[key]
            })
        
        # Common keys with different values
        for key in keys1 & keys2:
            if obj1[key] != obj2[key]:
                sub_diffs = _find_differences(obj1[key], obj2[key], path + [str(key)])
                differences.extend(sub_diffs)
    
    elif isinstance(obj1, list):
        for i in range(max(len(obj1), len(obj2))):
            if i >= len(obj1):
                differences.append({
                    "path": ".".join(path + [f"[{i}]"]) if path else f"[{i}]",
                    "type": "item_added",
                    "value1": None,
                    "value2": obj2[i]
                })
            elif i >= len(obj2):
                differences.append({
                    "path": ".".join(path + [f"[{i}]"]) if path else f"[{i}]",
                    "type": "item_removed",
                    "value1": obj1[i],
                    "value2": None
                })
            elif obj1[i] != obj2[i]:
                sub_diffs = _find_differences(obj1[i], obj2[i], path + [f"[{i}]"])
                differences.extend(sub_diffs)
    
    else:
        # Scalar values
        if obj1 != obj2:
            differences.append({
                "path": ".".join(path) if path else "root",
                "type": "value_changed",
                "value1": obj1,
                "value2": obj2
            })
    
    return differences
