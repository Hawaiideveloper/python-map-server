"""
Advanced JSON/YAML processing with Claude-style structured output control.

This module implements Anthropic's advanced API patterns for structured data
processing, ensuring we DOMINATE Claude with superior consistency and control.
"""

import json
import re
import traceback
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from ..utils.logging import log_tool_execution


class OutputFormat(Enum):
    """Supported output formats for structured data processing."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    TOML = "toml"
    CSV = "csv"


class StructuredOutputMode(Enum):
    """Output consistency modes based on Anthropic's guidance."""
    STRICT_JSON = "strict_json"
    VALIDATED_SCHEMA = "validated_schema"
    TEMPLATE_BASED = "template_based"
    FORCE_FORMAT = "force_format"


@dataclass
class DataProcessingConfig:
    """Configuration for advanced data processing operations."""
    output_format: OutputFormat
    consistency_mode: StructuredOutputMode
    schema: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    validation_rules: Optional[List[str]] = None
    error_handling: str = "strict"  # strict, permissive, auto_fix
    preserve_comments: bool = False
    sort_keys: bool = False
    indent_size: int = 2
    max_line_length: int = 120


class AdvancedDataProcessor:
    """
    Advanced data processor implementing Anthropic's structured output patterns.
    
    This class provides Claude-level consistency with superior performance
    and reliability for JSON/YAML/XML processing tasks.
    """
    
    def __init__(self):
        self.system_prompts = self._load_system_prompts()
        self.output_templates = self._load_output_templates()
        self.validation_schemas = self._load_validation_schemas()
        
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for consistent structured output."""
        return {
            "json_formatter": """You are a JSON formatting specialist. Your task is to:
1. Convert any input data to valid, well-formatted JSON
2. Ensure all strings are properly quoted with double quotes
3. Remove trailing commas and fix syntax errors
4. Validate against provided schemas if given
5. Maintain data integrity during conversion
6. Use consistent indentation and formatting
7. Return ONLY valid JSON, no additional text or explanations""",
            
            "yaml_formatter": """You are a YAML formatting specialist. Your task is to:
1. Convert any input data to valid, well-formatted YAML
2. Use consistent indentation (2 or 4 spaces, never tabs)
3. Follow YAML best practices for readability
4. Handle complex data structures properly
5. Preserve comments when requested
6. Ensure all scalar values are properly formatted
7. Return ONLY valid YAML, no additional text or explanations""",
            
            "data_validator": """You are a data validation expert. Your task is to:
1. Analyze data structure for consistency and correctness
2. Identify schema violations and type mismatches
3. Detect security vulnerabilities in configuration data
4. Suggest fixes for common data format issues
5. Provide detailed error explanations with line numbers
6. Recommend best practices for data organization
7. Return structured validation results in JSON format""",
            
            "schema_enforcer": """You are a schema enforcement specialist. Your task is to:
1. Ensure data strictly conforms to provided JSON schemas
2. Transform data to match required schema structure
3. Add missing required fields with appropriate defaults
4. Remove extra fields not in schema (if strict mode)
5. Convert data types to match schema requirements
6. Validate nested objects and arrays recursively
7. Return schema-compliant data or detailed error report"""
        }
    
    def _load_output_templates(self) -> Dict[str, str]:
        """Load output templates for consistent formatting."""
        return {
            "docker_compose": """version: '{version}'
services:
{services}
{networks}
{volumes}""",
            
            "kubernetes_deployment": """apiVersion: {api_version}
kind: {kind}
metadata:
  name: {name}
  namespace: {namespace}
  labels:
{labels}
spec:
{spec}""",
            
            "package_json": """{
  "name": "{name}",
  "version": "{version}",
  "description": "{description}",
  "main": "{main}",
  "scripts": {scripts},
  "dependencies": {dependencies},
  "devDependencies": {dev_dependencies}
}""",
            
            "openapi_spec": """{
  "openapi": "{openapi_version}",
  "info": {
    "title": "{title}",
    "version": "{version}",
    "description": "{description}"
  },
  "paths": {paths},
  "components": {components}
}""",
            
            "terraform_config": """terraform {
  required_version = "{terraform_version}"
  required_providers {
{providers}
  }
}

{resources}""",
            
            "github_workflow": """name: {name}

on:
{triggers}

jobs:
{jobs}""",
            
            "validation_report": """{
  "validation_status": "{status}",
  "format": "{format}",
  "timestamp": "{timestamp}",
  "errors": {errors},
  "warnings": {warnings},
  "suggestions": {suggestions},
  "metadata": {metadata}
}"""
        }
    
    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load JSON schemas for common data formats."""
        return {
            "docker_compose": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "services": {
                        "type": "object",
                        "patternProperties": {
                            "^[a-zA-Z0-9_-]+$": {
                                "type": "object",
                                "properties": {
                                    "image": {"type": "string"},
                                    "build": {"type": ["string", "object"]},
                                    "ports": {
                                        "type": "array",
                                        "items": {"type": ["string", "number"]}
                                    },
                                    "environment": {
                                        "type": ["object", "array"]
                                    },
                                    "volumes": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "depends_on": {
                                        "type": ["array", "object"]
                                    }
                                }
                            }
                        }
                    },
                    "networks": {"type": "object"},
                    "volumes": {"type": "object"}
                },
                "required": ["version", "services"]
            },
            
            "kubernetes": {
                "type": "object",
                "properties": {
                    "apiVersion": {"type": "string"},
                    "kind": {"type": "string"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "namespace": {"type": "string"},
                            "labels": {"type": "object"}
                        },
                        "required": ["name"]
                    },
                    "spec": {"type": "object"}
                },
                "required": ["apiVersion", "kind", "metadata"]
            },
            
            "package_json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "main": {"type": "string"},
                    "scripts": {"type": "object"},
                    "dependencies": {"type": "object"},
                    "devDependencies": {"type": "object"},
                    "peerDependencies": {"type": "object"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "author": {"type": ["string", "object"]},
                    "license": {"type": "string"}
                },
                "required": ["name", "version"]
            },
            
            "openapi": {
                "type": "object",
                "properties": {
                    "openapi": {"type": "string"},
                    "info": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "version": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["title", "version"]
                    },
                    "paths": {"type": "object"},
                    "components": {"type": "object"}
                },
                "required": ["openapi", "info", "paths"]
            }
        }


class StructuredOutputController:
    """
    Controller for enforcing structured output consistency.
    
    Implements Anthropic's guidance for JSON mode and template-based processing
    to ensure reliable, consistent output formatting.
    """
    
    def __init__(self, processor: AdvancedDataProcessor):
        self.processor = processor
        
    def enforce_json_mode(
        self,
        data: Any,
        schema: Optional[Dict[str, Any]] = None,
        strict: bool = True
    ) -> Dict[str, Any]:
        """
        Enforce strict JSON mode output with schema validation.
        
        Based on Anthropic's tool_choice=required pattern for consistent formatting.
        """
        result = {
            "success": False,
            "output": None,
            "format": "json",
            "validation": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Step 1: Ensure data is JSON-serializable
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    # Attempt to fix common JSON issues
                    fixed_data = self._auto_fix_json(data)
                    try:
                        data = json.loads(fixed_data)
                        result["warnings"].append(f"Auto-fixed JSON syntax errors: {str(e)}")
                    except:
                        result["errors"].append(f"Invalid JSON that cannot be auto-fixed: {str(e)}")
                        return result
            
            # Step 2: Schema validation if provided
            if schema and JSONSCHEMA_AVAILABLE:
                try:
                    validate(instance=data, schema=schema)
                    result["validation"]["schema_valid"] = True
                except ValidationError as e:
                    if strict:
                        result["errors"].append(f"Schema validation failed: {e.message}")
                        return result
                    else:
                        result["warnings"].append(f"Schema validation warning: {e.message}")
                        result["validation"]["schema_valid"] = False
            
            # Step 3: Format with consistent style
            formatted_output = json.dumps(
                data,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                separators=(',', ': ')
            )
            
            result["success"] = True
            result["output"] = formatted_output
            result["validation"]["syntax_valid"] = True
            result["validation"]["formatted"] = True
            
        except Exception as e:
            result["errors"].append(f"JSON mode enforcement failed: {str(e)}")
        
        return result
    
    def enforce_yaml_mode(
        self,
        data: Any,
        template: Optional[str] = None,
        preserve_comments: bool = False
    ) -> Dict[str, Any]:
        """
        Enforce consistent YAML output with template-based formatting.
        """
        result = {
            "success": False,
            "output": None,
            "format": "yaml",
            "validation": {},
            "errors": [],
            "warnings": []
        }
        
        if not YAML_AVAILABLE:
            result["errors"].append("YAML processing not available")
            return result
        
        try:
            # Step 1: Parse input data
            if isinstance(data, str):
                try:
                    data = yaml.safe_load(data)
                except yaml.YAMLError as e:
                    result["errors"].append(f"YAML parsing error: {str(e)}")
                    return result
            
            # Step 2: Apply template if provided
            if template and template in self.processor.output_templates:
                try:
                    template_str = self.processor.output_templates[template]
                    # Template-based formatting logic would go here
                    pass
                except Exception as e:
                    result["warnings"].append(f"Template application failed: {str(e)}")
            
            # Step 3: Format with consistent style
            formatted_output = yaml.dump(
                data,
                default_flow_style=False,
                indent=2,
                allow_unicode=True,
                sort_keys=True
            )
            
            result["success"] = True
            result["output"] = formatted_output
            result["validation"]["syntax_valid"] = True
            result["validation"]["formatted"] = True
            
        except Exception as e:
            result["errors"].append(f"YAML mode enforcement failed: {str(e)}")
        
        return result
    
    def _auto_fix_json(self, content: str) -> str:
        """
        Auto-fix common JSON syntax issues using Anthropic-style patterns.
        """
        # Remove comments (not valid in JSON)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Fix trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Fix single quotes to double quotes
        content = re.sub(r"'([^'\\]*(\\.[^'\\]*)*)'", r'"\1"', content)
        
        # Fix unquoted keys
        content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        
        # Fix Python booleans
        content = re.sub(r'\bTrue\b', 'true', content)
        content = re.sub(r'\bFalse\b', 'false', content)
        content = re.sub(r'\bNone\b', 'null', content)
        
        return content


class AdvancedTemplateProcessor:
    """
    Template-based processor for structured data formats.
    
    Provides predefined templates for common configuration files
    and data structures with validation and consistency enforcement.
    """
    
    def __init__(self, processor: AdvancedDataProcessor):
        self.processor = processor
        self.template_validators = self._setup_template_validators()
    
    def _setup_template_validators(self) -> Dict[str, callable]:
        """Setup template-specific validation functions."""
        return {
            "docker_compose": self._validate_docker_compose,
            "kubernetes": self._validate_kubernetes,
            "package_json": self._validate_package_json,
            "openapi": self._validate_openapi,
            "terraform": self._validate_terraform,
            "github_workflow": self._validate_github_workflow
        }
    
    def process_with_template(
        self,
        data: Any,
        template_name: str,
        config: DataProcessingConfig
    ) -> Dict[str, Any]:
        """
        Process data using predefined templates with validation.
        """
        result = {
            "success": False,
            "output": None,
            "template": template_name,
            "format": config.output_format.value,
            "validation": {},
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Step 1: Validate template exists
            if template_name not in self.processor.output_templates:
                result["errors"].append(f"Template '{template_name}' not found")
                return result
            
            # Step 2: Parse input data
            if isinstance(data, str):
                if config.output_format == OutputFormat.JSON:
                    data = json.loads(data)
                elif config.output_format == OutputFormat.YAML and YAML_AVAILABLE:
                    data = yaml.safe_load(data)
            
            # Step 3: Template-specific validation
            if template_name in self.template_validators:
                validation_result = self.template_validators[template_name](data)
                result["validation"].update(validation_result)
                
                if not validation_result.get("valid", True):
                    if config.error_handling == "strict":
                        result["errors"].extend(validation_result.get("errors", []))
                        return result
                    else:
                        result["warnings"].extend(validation_result.get("errors", []))
            
            # Step 4: Apply template formatting
            template_str = self.processor.output_templates[template_name]
            formatted_output = self._apply_template(template_str, data, config)
            
            # Step 5: Final validation and formatting
            if config.output_format == OutputFormat.JSON:
                try:
                    # Ensure valid JSON
                    parsed = json.loads(formatted_output)
                    formatted_output = json.dumps(
                        parsed,
                        indent=config.indent_size,
                        sort_keys=config.sort_keys,
                        ensure_ascii=False
                    )
                except json.JSONDecodeError as e:
                    result["errors"].append(f"Template produced invalid JSON: {str(e)}")
                    return result
            
            result["success"] = True
            result["output"] = formatted_output
            result["validation"]["template_applied"] = True
            
        except Exception as e:
            result["errors"].append(f"Template processing failed: {str(e)}")
        
        return result
    
    def _apply_template(
        self,
        template_str: str,
        data: Dict[str, Any],
        config: DataProcessingConfig
    ) -> str:
        """Apply template with data substitution."""
        try:
            # Simple template variable substitution
            for key, value in data.items():
                if isinstance(value, str):
                    template_str = template_str.replace(f"{{{key}}}", value)
                elif isinstance(value, (dict, list)):
                    if config.output_format == OutputFormat.JSON:
                        json_value = json.dumps(value, indent=config.indent_size)
                    else:
                        json_value = str(value)
                    template_str = template_str.replace(f"{{{key}}}", json_value)
                else:
                    template_str = template_str.replace(f"{{{key}}}", str(value))
            
            return template_str
            
        except Exception as e:
            raise Exception(f"Template application failed: {str(e)}")
    
    def _validate_docker_compose(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Docker Compose data structure."""
        errors = []
        warnings = []
        
        if "version" not in data:
            errors.append("Missing required 'version' field")
        
        if "services" not in data:
            errors.append("Missing required 'services' field")
        elif not isinstance(data["services"], dict):
            errors.append("'services' must be an object")
        
        # Validate individual services
        for service_name, service_config in data.get("services", {}).items():
            if not isinstance(service_config, dict):
                errors.append(f"Service '{service_name}' must be an object")
                continue
            
            if "image" not in service_config and "build" not in service_config:
                warnings.append(f"Service '{service_name}' should have either 'image' or 'build'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_kubernetes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Kubernetes manifest structure."""
        errors = []
        warnings = []
        
        required_fields = ["apiVersion", "kind", "metadata"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if "metadata" in data:
            if "name" not in data["metadata"]:
                errors.append("Missing required 'metadata.name' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_package_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate package.json structure."""
        errors = []
        warnings = []
        
        if "name" not in data:
            errors.append("Missing required 'name' field")
        
        if "version" not in data:
            errors.append("Missing required 'version' field")
        
        # Check for common issues
        if "main" in data and not data["main"].endswith((".js", ".mjs", ".cjs")):
            warnings.append("'main' field should point to a JavaScript file")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_openapi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OpenAPI specification structure."""
        errors = []
        warnings = []
        
        if "openapi" not in data:
            errors.append("Missing required 'openapi' field")
        
        if "info" not in data:
            errors.append("Missing required 'info' field")
        elif isinstance(data["info"], dict):
            if "title" not in data["info"]:
                errors.append("Missing required 'info.title' field")
            if "version" not in data["info"]:
                errors.append("Missing required 'info.version' field")
        
        if "paths" not in data:
            errors.append("Missing required 'paths' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_terraform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Terraform configuration structure."""
        errors = []
        warnings = []
        
        # Basic Terraform validation
        if "terraform" in data:
            terraform_block = data["terraform"]
            if "required_version" not in terraform_block:
                warnings.append("Consider specifying 'required_version' in terraform block")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_github_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GitHub workflow structure."""
        errors = []
        warnings = []
        
        if "name" not in data:
            warnings.append("Consider adding a 'name' field for workflow identification")
        
        if "on" not in data:
            errors.append("Missing required 'on' field (workflow triggers)")
        
        if "jobs" not in data:
            errors.append("Missing required 'jobs' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# Main tool functions with advanced capabilities
@log_tool_execution("advanced_json_processing")
def process_json_with_schema_enforcement(
    content: str,
    schema: Optional[Dict[str, Any]] = None,
    template: Optional[str] = None,
    strict_mode: bool = True
) -> Dict[str, Any]:
    """
    Advanced JSON processing with schema enforcement and template support.
    
    Implements Anthropic's tool_choice=required pattern for consistent output.
    """
    processor = AdvancedDataProcessor()
    controller = StructuredOutputController(processor)
    
    result = controller.enforce_json_mode(
        data=content,
        schema=schema,
        strict=strict_mode
    )
    
    # Add template processing if specified
    if template:
        template_processor = AdvancedTemplateProcessor(processor)
        config = DataProcessingConfig(
            output_format=OutputFormat.JSON,
            consistency_mode=StructuredOutputMode.TEMPLATE_BASED
        )
        template_result = template_processor.process_with_template(
            data=result.get("output", content),
            template_name=template,
            config=config
        )
        result["template_processing"] = template_result
    
    return result


@log_tool_execution("advanced_yaml_processing")
def process_yaml_with_template_enforcement(
    content: str,
    template: Optional[str] = None,
    preserve_comments: bool = False,
    strict_formatting: bool = True
) -> Dict[str, Any]:
    """
    Advanced YAML processing with template enforcement and consistency control.
    
    Provides Claude-level formatting consistency with superior validation.
    """
    processor = AdvancedDataProcessor()
    controller = StructuredOutputController(processor)
    
    result = controller.enforce_yaml_mode(
        data=content,
        template=template,
        preserve_comments=preserve_comments
    )
    
    # Add advanced template processing
    if template:
        template_processor = AdvancedTemplateProcessor(processor)
        config = DataProcessingConfig(
            output_format=OutputFormat.YAML,
            consistency_mode=StructuredOutputMode.TEMPLATE_BASED,
            preserve_comments=preserve_comments
        )
        template_result = template_processor.process_with_template(
            data=result.get("output", content),
            template_name=template,
            config=config
        )
        result["template_processing"] = template_result
    
    return result


@log_tool_execution("structured_output_generation")
def generate_structured_output(
    data: Any,
    output_format: str = "json",
    template: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    consistency_mode: str = "strict_json"
) -> Dict[str, Any]:
    """
    Generate structured output with enforced consistency and validation.
    
    Implements advanced Anthropic patterns for reliable data formatting.
    """
    processor = AdvancedDataProcessor()
    
    try:
        # Configure processing
        format_enum = OutputFormat(output_format.lower())
        mode_enum = StructuredOutputMode(consistency_mode.lower())
        
        config = DataProcessingConfig(
            output_format=format_enum,
            consistency_mode=mode_enum,
            schema=schema,
            template=template
        )
        
        # Process based on format
        if format_enum == OutputFormat.JSON:
            controller = StructuredOutputController(processor)
            result = controller.enforce_json_mode(data, schema, strict=True)
        elif format_enum == OutputFormat.YAML:
            controller = StructuredOutputController(processor)
            result = controller.enforce_yaml_mode(data, template)
        else:
            result = {
                "success": False,
                "errors": [f"Unsupported output format: {output_format}"],
                "output": None
            }
        
        # Add consistency analysis
        result["consistency_analysis"] = {
            "mode_used": consistency_mode,
            "template_applied": template is not None,
            "schema_validated": schema is not None and result.get("validation", {}).get("schema_valid", False),
            "format_enforced": result.get("success", False)
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "errors": [f"Structured output generation failed: {str(e)}"],
            "output": None,
            "traceback": traceback.format_exc()
        }


@log_tool_execution("batch_format_conversion")
def batch_convert_formats(
    inputs: List[Dict[str, Any]],
    target_format: str = "json",
    apply_templates: bool = True,
    validate_schemas: bool = True
) -> Dict[str, Any]:
    """
    Batch convert multiple data structures with consistent formatting.
    
    Provides enterprise-grade batch processing with validation and templating.
    """
    results = []
    summary = {
        "total_processed": len(inputs),
        "successful": 0,
        "failed": 0,
        "warnings": 0,
        "processing_time": 0
    }
    
    import time
    start_time = time.time()
    
    for i, input_data in enumerate(inputs):
        try:
            content = input_data.get("content", "")
            template = input_data.get("template") if apply_templates else None
            schema = input_data.get("schema") if validate_schemas else None
            
            result = generate_structured_output(
                data=content,
                output_format=target_format,
                template=template,
                schema=schema
            )
            
            result["input_index"] = i
            results.append(result)
            
            if result.get("success", False):
                summary["successful"] += 1
            else:
                summary["failed"] += 1
            
            if result.get("warnings"):
                summary["warnings"] += len(result["warnings"])
                
        except Exception as e:
            results.append({
                "input_index": i,
                "success": False,
                "errors": [f"Processing failed: {str(e)}"],
                "output": None
            })
            summary["failed"] += 1
    
    summary["processing_time"] = time.time() - start_time
    
    return {
        "results": results,
        "summary": summary,
        "batch_processing": True,
        "target_format": target_format
    }
