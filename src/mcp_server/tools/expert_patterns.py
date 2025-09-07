"""
Expert-level Python patterns and architectural wisdom.

This module provides deep architectural patterns, design principles,
and expert-level code analysis that a 30-year Python veteran would use.
"""

import ast
import inspect
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("analyze_architecture")
def analyze_code_architecture(code: str, project_type: str = "general") -> Dict[str, Any]:
    """
    Analyze code architecture with expert-level insights.
    
    Args:
        code: Python code to analyze
        project_type: Type of project (web, ml, data, enterprise, library)
        
    Returns:
        Dict with architectural analysis and expert recommendations
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Architectural analysis
        analysis = {
            "design_patterns": detect_design_patterns(tree, code),
            "solid_principles": analyze_solid_principles(tree, code),
            "architectural_smells": detect_architectural_smells(tree, code),
            "coupling_analysis": analyze_coupling(tree),
            "cohesion_analysis": analyze_cohesion(tree),
            "complexity_metrics": calculate_complexity_metrics(tree, code),
            "maintainability_score": calculate_maintainability_score(tree, code),
            "expert_recommendations": generate_expert_recommendations(tree, code, project_type)
        }
        
        # Project-specific analysis
        if project_type != "general":
            analysis["project_specific"] = analyze_project_specific_patterns(tree, code, project_type)
            
        return {
            "status": "success",
            "result": analysis
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "analyze_architecture"
        }


@log_tool_execution("generate_expert_code")
def generate_expert_code_templates(pattern_type: str, use_case: str) -> Dict[str, Any]:
    """
    Generate expert-level code templates and patterns.
    
    Args:
        pattern_type: Design pattern type (singleton, factory, observer, etc.)
        use_case: Specific use case or domain
        
    Returns:
        Dict with code templates and implementation guidance
    """
    try:
        templates = EXPERT_PATTERNS.get(pattern_type, {})
        
        if not templates:
            available_patterns = list(EXPERT_PATTERNS.keys())
            return {
                "status": "error",
                "error": f"Unknown pattern: {pattern_type}",
                "available_patterns": available_patterns
            }
            
        # Generate context-specific template
        template = templates.get("template", "")
        examples = templates.get("examples", [])
        best_practices = templates.get("best_practices", [])
        
        # Customize for use case
        customized_template = customize_template_for_use_case(template, use_case)
        
        return {
            "status": "success",
            "result": {
                "pattern_type": pattern_type,
                "use_case": use_case,
                "template": customized_template,
                "examples": examples,
                "best_practices": best_practices,
                "when_to_use": templates.get("when_to_use", ""),
                "when_not_to_use": templates.get("when_not_to_use", ""),
                "common_mistakes": templates.get("common_mistakes", [])
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "generate_expert_code"
        }


@log_tool_execution("async_analysis")
def analyze_async_patterns(code: str) -> Dict[str, Any]:
    """
    Analyze asynchronous programming patterns and suggest improvements.
    
    Args:
        code: Python code with async/await patterns
        
    Returns:
        Dict with async analysis and recommendations
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Async pattern analysis
        async_functions = []
        await_usages = []
        async_context_managers = []
        async_generators = []
        potential_deadlocks = []
        performance_issues = []
        
        # Analyze AST for async patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "has_proper_error_handling": has_async_error_handling(node),
                    "uses_context_managers": uses_async_context_managers(node),
                    "complexity": calculate_async_complexity(node)
                })
                
            elif isinstance(node, ast.Await):
                await_usages.append({
                    "line": getattr(node, 'lineno', 0),
                    "in_loop": is_await_in_loop(node, tree),
                    "proper_exception_handling": has_await_exception_handling(node, tree)
                })
                
        # Detect async anti-patterns
        anti_patterns = detect_async_antipatterns(code, tree)
        
        # Generate async optimization suggestions
        optimizations = generate_async_optimizations(async_functions, await_usages, code)
        
        # Concurrency safety analysis
        safety_analysis = analyze_concurrency_safety(tree, code)
        
        return {
            "status": "success",
            "result": {
                "async_functions": async_functions,
                "await_usages": await_usages,
                "anti_patterns": anti_patterns,
                "optimizations": optimizations,
                "safety_analysis": safety_analysis,
                "expert_recommendations": generate_async_expert_recommendations(async_functions, anti_patterns)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "async_analysis"
        }


@log_tool_execution("enterprise_patterns")
def analyze_enterprise_patterns(code: str, codebase_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze enterprise-level patterns and practices.
    
    Args:
        code: Python code to analyze
        codebase_context: Additional context about the codebase
        
    Returns:
        Dict with enterprise pattern analysis
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        tree = ast.parse(code)
        
        # Enterprise pattern analysis
        analysis = {
            "dependency_injection": analyze_dependency_injection(tree, code),
            "error_handling_strategy": analyze_error_handling_strategy(tree, code),
            "logging_patterns": analyze_logging_patterns(tree, code),
            "configuration_management": analyze_config_patterns(tree, code),
            "caching_strategies": analyze_caching_patterns(tree, code),
            "api_design_patterns": analyze_api_patterns(tree, code),
            "data_access_patterns": analyze_data_access_patterns(tree, code),
            "security_patterns": analyze_security_patterns(tree, code),
            "testing_patterns": analyze_testing_patterns(tree, code),
            "scalability_concerns": analyze_scalability_patterns(tree, code)
        }
        
        # Generate enterprise recommendations
        enterprise_recommendations = generate_enterprise_recommendations(analysis, codebase_context)
        
        return {
            "status": "success",
            "result": {
                **analysis,
                "enterprise_score": calculate_enterprise_score(analysis),
                "recommendations": enterprise_recommendations,
                "production_readiness": assess_production_readiness(analysis)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "enterprise_patterns"
        }


# Expert Pattern Templates
EXPERT_PATTERNS = {
    "singleton": {
        "template": '''
class Singleton:
    """Thread-safe singleton implementation with lazy initialization."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # Initialize only once
            self._initialized = True
            # Your initialization code here
''',
        "when_to_use": "When you need exactly one instance globally (logging, config, caching)",
        "when_not_to_use": "When you need multiple instances or testing becomes difficult",
        "common_mistakes": ["Not thread-safe", "Difficult to test", "Hidden dependencies"],
        "best_practices": ["Use dependency injection instead when possible", "Make thread-safe", "Consider using modules instead"]
    },
    
    "factory": {
        "template": '''
from abc import ABC, abstractmethod
from typing import Dict, Type

class Product(ABC):
    """Abstract product interface."""
    @abstractmethod
    def operation(self) -> str:
        pass

class ConcreteProductA(Product):
    def operation(self) -> str:
        return "Result of ConcreteProductA"

class ConcreteProductB(Product):
    def operation(self) -> str:
        return "Result of ConcreteProductB"

class Factory:
    """Factory for creating products."""
    _products: Dict[str, Type[Product]] = {
        "A": ConcreteProductA,
        "B": ConcreteProductB,
    }
    
    @classmethod
    def create_product(cls, product_type: str) -> Product:
        product_class = cls._products.get(product_type)
        if not product_class:
            raise ValueError(f"Unknown product type: {product_type}")
        return product_class()
    
    @classmethod
    def register_product(cls, name: str, product_class: Type[Product]) -> None:
        cls._products[name] = product_class
''',
        "when_to_use": "When object creation is complex or you need to decouple creation from usage",
        "when_not_to_use": "For simple object creation that doesn't vary",
        "best_practices": ["Use type hints", "Make extensible", "Consider using protocols"]
    },
    
    "observer": {
        "template": '''
from abc import ABC, abstractmethod
from typing import List, Any
from weakref import WeakSet

class Observer(ABC):
    """Abstract observer interface."""
    @abstractmethod
    def update(self, subject: 'Subject', event: str, data: Any = None) -> None:
        pass

class Subject:
    """Subject that observers can subscribe to."""
    
    def __init__(self):
        self._observers: WeakSet[Observer] = WeakSet()
    
    def attach(self, observer: Observer) -> None:
        self._observers.add(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.discard(observer)
    
    def notify(self, event: str, data: Any = None) -> None:
        for observer in self._observers.copy():
            try:
                observer.update(self, event, data)
            except Exception as e:
                # Log error but don't stop other notifications
                print(f"Observer notification failed: {e}")
''',
        "when_to_use": "When changes to one object require updating multiple dependent objects",
        "when_not_to_use": "When the relationship is simple or performance is critical",
        "best_practices": ["Use weak references to prevent memory leaks", "Handle observer errors gracefully", "Consider using events or signals"]
    },
    
    "strategy": {
        "template": '''
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

class Strategy(ABC):
    """Abstract strategy interface."""
    @abstractmethod
    def execute(self, data: Any) -> Any:
        pass

class ConcreteStrategyA(Strategy):
    def execute(self, data: Any) -> Any:
        return f"Strategy A processing: {data}"

class ConcreteStrategyB(Strategy):
    def execute(self, data: Any) -> Any:
        return f"Strategy B processing: {data}"

class Context:
    """Context that uses a strategy."""
    
    def __init__(self, strategy: Strategy = None):
        self._strategy = strategy or ConcreteStrategyA()
    
    def set_strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy
    
    def execute_strategy(self, data: Any) -> Any:
        return self._strategy.execute(data)

# Strategy registry for dynamic loading
class StrategyRegistry:
    _strategies: Dict[str, Type[Strategy]] = {}
    
    @classmethod
    def register(cls, name: str, strategy_class: Type[Strategy]) -> None:
        cls._strategies[name] = strategy_class
    
    @classmethod
    def get_strategy(cls, name: str) -> Strategy:
        strategy_class = cls._strategies.get(name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {name}")
        return strategy_class()
''',
        "when_to_use": "When you have multiple ways to perform a task and want to switch between them",
        "when_not_to_use": "When there's only one way to do something or behavior doesn't vary",
        "best_practices": ["Make strategies stateless when possible", "Use dependency injection", "Consider using functions instead of classes for simple strategies"]
    }
}


# Helper functions for architectural analysis
def detect_design_patterns(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect design patterns in code."""
    patterns = []
    
    # Singleton detection
    if "def __new__" in code and "_instance" in code:
        patterns.append({
            "pattern": "singleton",
            "confidence": 0.8,
            "location": "class definition",
            "note": "Detected singleton pattern implementation"
        })
    
    # Factory detection
    if "create_" in code or "factory" in code.lower():
        patterns.append({
            "pattern": "factory",
            "confidence": 0.6,
            "location": "method names",
            "note": "Possible factory pattern based on naming"
        })
    
    # Observer detection
    if ("attach" in code and "detach" in code and "notify" in code) or "observer" in code.lower():
        patterns.append({
            "pattern": "observer",
            "confidence": 0.7,
            "location": "method definitions",
            "note": "Observer pattern detected"
        })
    
    return patterns


def analyze_solid_principles(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze adherence to SOLID principles."""
    violations = []
    
    # Single Responsibility Principle
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
            if method_count > 10:
                violations.append({
                    "principle": "SRP",
                    "class": node.name,
                    "issue": f"Class has {method_count} methods, possibly too many responsibilities",
                    "severity": "medium"
                })
    
    # Open/Closed Principle
    # Look for direct modifications instead of extensions
    if "if isinstance(" in code and "type(" in code:
        violations.append({
            "principle": "OCP",
            "issue": "Type checking suggests code may not be open for extension",
            "severity": "low"
        })
    
    return {
        "violations": violations,
        "solid_score": max(0, 100 - len(violations) * 10),
        "recommendations": generate_solid_recommendations(violations)
    }


def detect_architectural_smells(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect architectural code smells."""
    smells = []
    
    # God class detection
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            lines = getattr(node, 'end_lineno', 0) - node.lineno
            if lines > 200:
                smells.append({
                    "type": "god_class",
                    "class": node.name,
                    "lines": lines,
                    "severity": "high",
                    "description": "Class is too large and likely has too many responsibilities"
                })
    
    # Circular dependencies (simplified check)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    if len(imports) > 20:
        smells.append({
            "type": "excessive_imports",
            "count": len(imports),
            "severity": "medium",
            "description": "Too many imports may indicate tight coupling"
        })
    
    return smells


def analyze_coupling(tree: ast.AST) -> Dict[str, Any]:
    """Analyze coupling between components."""
    # Simplified coupling analysis
    imports = []
    function_calls = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
        elif isinstance(node, ast.Call):
            function_calls.append(node)
    
    return {
        "import_coupling": len(imports),
        "call_coupling": len(function_calls),
        "coupling_level": "high" if len(imports) > 15 else "medium" if len(imports) > 8 else "low"
    }


def analyze_cohesion(tree: ast.AST) -> Dict[str, Any]:
    """Analyze cohesion within classes."""
    cohesion_scores = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Simple cohesion metric based on method interactions
            methods = [item for item in node.body if isinstance(item, ast.FunctionDef)]
            if methods:
                # Calculate how methods interact with instance variables
                cohesion_score = calculate_class_cohesion(node)
                cohesion_scores.append({
                    "class": node.name,
                    "score": cohesion_score,
                    "methods": len(methods)
                })
    
    avg_cohesion = sum(score["score"] for score in cohesion_scores) / len(cohesion_scores) if cohesion_scores else 0
    
    return {
        "class_cohesion": cohesion_scores,
        "average_cohesion": avg_cohesion,
        "cohesion_level": "high" if avg_cohesion > 0.7 else "medium" if avg_cohesion > 0.4 else "low"
    }


def calculate_complexity_metrics(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Calculate various complexity metrics."""
    # Cyclomatic complexity
    cyclomatic = 1  # Base complexity
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            cyclomatic += 1
        elif isinstance(node, ast.BoolOp):
            cyclomatic += len(node.values) - 1
    
    # Halstead metrics (simplified)
    operators = len([node for node in ast.walk(tree) if isinstance(node, ast.operator)])
    operands = len([node for node in ast.walk(tree) if isinstance(node, ast.Name)])
    
    lines_of_code = len([line for line in code.split('\n') if line.strip()])
    
    return {
        "cyclomatic_complexity": cyclomatic,
        "halstead_operators": operators,
        "halstead_operands": operands,
        "lines_of_code": lines_of_code,
        "complexity_rating": get_complexity_rating(cyclomatic)
    }


def get_complexity_rating(cyclomatic: int) -> str:
    """Get complexity rating based on cyclomatic complexity."""
    if cyclomatic <= 10:
        return "low"
    elif cyclomatic <= 20:
        return "moderate"
    elif cyclomatic <= 50:
        return "high"
    else:
        return "very_high"


def calculate_maintainability_score(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Calculate maintainability score based on various factors."""
    factors = {
        "documentation": calculate_documentation_score(tree, code),
        "naming": calculate_naming_score(tree),
        "complexity": calculate_complexity_score(tree),
        "structure": calculate_structure_score(tree, code)
    }
    
    # Weighted average
    weights = {"documentation": 0.3, "naming": 0.2, "complexity": 0.3, "structure": 0.2}
    overall_score = sum(factors[key] * weights[key] for key in factors)
    
    return {
        "overall_score": overall_score,
        "factors": factors,
        "maintainability_level": get_maintainability_level(overall_score)
    }


def get_maintainability_level(score: float) -> str:
    """Get maintainability level based on score."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "fair"
    else:
        return "poor"


def generate_expert_recommendations(tree: ast.AST, code: str, project_type: str) -> List[Dict[str, Any]]:
    """Generate expert-level recommendations."""
    recommendations = []
    
    # Check for missing error handling
    try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    if len(try_blocks) < len(functions) * 0.3:  # Less than 30% of functions have error handling
        recommendations.append({
            "category": "error_handling",
            "priority": "high",
            "title": "Insufficient Error Handling",
            "description": "Consider adding proper error handling to your functions",
            "expert_insight": "A seasoned developer always anticipates what can go wrong"
        })
    
    # Check for logging
    if "logging" not in code and "print(" in code:
        recommendations.append({
            "category": "logging",
            "priority": "medium",
            "title": "Use Proper Logging",
            "description": "Replace print statements with proper logging",
            "expert_insight": "Logging is essential for production debugging and monitoring"
        })
    
    # Project-specific recommendations
    if project_type == "web":
        if "request" in code and "validate" not in code:
            recommendations.append({
                "category": "security",
                "priority": "high",
                "title": "Input Validation Missing",
                "description": "Web applications must validate all input",
                "expert_insight": "Never trust user input - validate everything"
            })
    
    return recommendations


# Additional helper functions would be implemented here...
def calculate_documentation_score(tree: ast.AST, code: str) -> float:
    """Calculate documentation score."""
    docstring_count = 0
    function_count = 0
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_count += 1
            if ast.get_docstring(node):
                docstring_count += 1
    
    return (docstring_count / function_count * 100) if function_count > 0 else 100


def calculate_naming_score(tree: ast.AST) -> float:
    """Calculate naming quality score."""
    score = 100
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.name) < 3 or not node.name.islower():
                score -= 5
        elif isinstance(node, ast.ClassDef):
            if not node.name[0].isupper():
                score -= 5
                
    return max(0, score)


def calculate_complexity_score(tree: ast.AST) -> float:
    """Calculate complexity score (inverted - lower complexity = higher score)."""
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For)):
            complexity += 1
    
    return max(0, 100 - complexity * 2)


def calculate_structure_score(tree: ast.AST, code: str) -> float:
    """Calculate code structure score."""
    score = 100
    lines = code.split('\n')
    
    # Penalize very long lines
    for line in lines:
        if len(line) > 120:
            score -= 1
    
    # Reward good structure
    if "class " in code:
        score += 10
    if "def " in code:
        score += 5
        
    return max(0, min(100, score))


def calculate_class_cohesion(class_node: ast.ClassDef) -> float:
    """Calculate cohesion score for a class."""
    # Simplified cohesion calculation
    # Real implementation would analyze method interactions with instance variables
    methods = [item for item in class_node.body if isinstance(item, ast.FunctionDef)]
    if not methods:
        return 1.0
    
    # For now, return a placeholder calculation
    # Real implementation would be much more sophisticated
    return min(1.0, 1.0 / len(methods) * 5)


def generate_solid_recommendations(violations: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations for SOLID principle violations."""
    recommendations = []
    
    for violation in violations:
        if violation["principle"] == "SRP":
            recommendations.append("Consider breaking large classes into smaller, focused classes")
        elif violation["principle"] == "OCP":
            recommendations.append("Use polymorphism and inheritance instead of type checking")
            
    return recommendations


# Placeholder functions for async analysis
def has_async_error_handling(node: ast.AsyncFunctionDef) -> bool:
    """Check if async function has proper error handling."""
    for item in ast.walk(node):
        if isinstance(item, ast.Try):
            return True
    return False


def uses_async_context_managers(node: ast.AsyncFunctionDef) -> bool:
    """Check if function uses async context managers."""
    for item in ast.walk(node):
        if isinstance(item, ast.AsyncWith):
            return True
    return False


def calculate_async_complexity(node: ast.AsyncFunctionDef) -> int:
    """Calculate complexity of async function."""
    complexity = 1
    for item in ast.walk(node):
        if isinstance(item, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
    return complexity


def is_await_in_loop(await_node: ast.Await, tree: ast.AST) -> bool:
    """Check if await is inside a loop."""
    # Simplified implementation
    return "for " in str(await_node) or "while " in str(await_node)


def has_await_exception_handling(await_node: ast.Await, tree: ast.AST) -> bool:
    """Check if await has proper exception handling."""
    # Simplified implementation
    return True  # Placeholder


def detect_async_antipatterns(code: str, tree: ast.AST) -> List[Dict[str, Any]]:
    """Detect async anti-patterns."""
    antipatterns = []
    
    if "time.sleep" in code:
        antipatterns.append({
            "type": "blocking_sleep",
            "description": "Using time.sleep in async code blocks the event loop",
            "solution": "Use asyncio.sleep() instead"
        })
    
    if "requests." in code:
        antipatterns.append({
            "type": "blocking_http",
            "description": "Using synchronous requests in async code",
            "solution": "Use aiohttp or httpx for async HTTP requests"
        })
    
    return antipatterns


def generate_async_optimizations(async_functions: List[Dict], await_usages: List[Dict], code: str) -> List[Dict[str, Any]]:
    """Generate async optimization suggestions."""
    optimizations = []
    
    if len(await_usages) > 5:
        optimizations.append({
            "type": "gather_optimization",
            "description": "Consider using asyncio.gather() for concurrent operations",
            "benefit": "Significant performance improvement for I/O bound operations"
        })
    
    return optimizations


def analyze_concurrency_safety(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze concurrency safety."""
    return {
        "thread_safe": "threading" not in code or "Lock" in code,
        "race_conditions": [],
        "shared_state_issues": []
    }


def generate_async_expert_recommendations(async_functions: List[Dict], anti_patterns: List[Dict]) -> List[Dict[str, Any]]:
    """Generate expert recommendations for async code."""
    recommendations = []
    
    if anti_patterns:
        recommendations.append({
            "priority": "high",
            "title": "Fix Async Anti-patterns",
            "description": "Address blocking operations in async code",
            "expert_insight": "Async code should never block the event loop"
        })
    
    return recommendations


# Enterprise pattern analysis functions (simplified implementations)
def analyze_dependency_injection(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze dependency injection patterns."""
    return {"pattern_detected": "__init__" in code and "self." in code}


def analyze_error_handling_strategy(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze error handling strategy."""
    try_blocks = len([node for node in ast.walk(tree) if isinstance(node, ast.Try)])
    return {"try_blocks": try_blocks, "strategy": "defensive" if try_blocks > 0 else "optimistic"}


def analyze_logging_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze logging patterns."""
    return {"uses_logging": "logging" in code, "uses_print": "print(" in code}


def analyze_config_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze configuration management patterns."""
    return {"uses_env_vars": "os.environ" in code or "getenv" in code}


def analyze_caching_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze caching patterns."""
    return {"uses_caching": "cache" in code.lower() or "lru_cache" in code}


def analyze_api_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze API design patterns."""
    return {"rest_patterns": "request" in code, "graphql_patterns": "graphql" in code.lower()}


def analyze_data_access_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze data access patterns."""
    return {"uses_orm": any(orm in code.lower() for orm in ["sqlalchemy", "django", "peewee"])}


def analyze_security_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze security patterns."""
    return {"input_validation": "validate" in code, "authentication": "auth" in code.lower()}


def analyze_testing_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze testing patterns."""
    return {"has_tests": any(test in code.lower() for test in ["test_", "pytest", "unittest"])}


def analyze_scalability_patterns(tree: ast.AST, code: str) -> Dict[str, Any]:
    """Analyze scalability patterns."""
    return {"async_support": "async" in code, "caching": "cache" in code.lower()}


def calculate_enterprise_score(analysis: Dict[str, Any]) -> int:
    """Calculate enterprise readiness score."""
    score = 0
    if analysis["dependency_injection"]["pattern_detected"]:
        score += 20
    if analysis["error_handling_strategy"]["try_blocks"] > 0:
        score += 20
    if analysis["logging_patterns"]["uses_logging"]:
        score += 20
    if analysis["security_patterns"]["input_validation"]:
        score += 20
    if analysis["testing_patterns"]["has_tests"]:
        score += 20
    return score


def generate_enterprise_recommendations(analysis: Dict[str, Any], context: Optional[str]) -> List[Dict[str, Any]]:
    """Generate enterprise-level recommendations."""
    recommendations = []
    
    if not analysis["logging_patterns"]["uses_logging"]:
        recommendations.append({
            "category": "logging",
            "priority": "high",
            "title": "Implement Structured Logging",
            "description": "Use proper logging framework for production monitoring"
        })
    
    return recommendations


def assess_production_readiness(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess production readiness."""
    score = calculate_enterprise_score(analysis)
    readiness = "ready" if score >= 80 else "needs_work" if score >= 60 else "not_ready"
    
    return {
        "score": score,
        "readiness": readiness,
        "blockers": get_production_blockers(analysis)
    }


def get_production_blockers(analysis: Dict[str, Any]) -> List[str]:
    """Get production readiness blockers."""
    blockers = []
    
    if not analysis["error_handling_strategy"]["try_blocks"]:
        blockers.append("Insufficient error handling")
    if not analysis["logging_patterns"]["uses_logging"]:
        blockers.append("No proper logging")
    if not analysis["security_patterns"]["input_validation"]:
        blockers.append("Missing input validation")
        
    return blockers


def customize_template_for_use_case(template: str, use_case: str) -> str:
    """Customize template for specific use case."""
    # Simple customization - in practice this would be much more sophisticated
    if "web" in use_case.lower():
        template = template.replace("# Your initialization code here", "# Web service initialization")
    elif "ml" in use_case.lower():
        template = template.replace("# Your initialization code here", "# ML model initialization")
    
    return template


def analyze_project_specific_patterns(tree: ast.AST, code: str, project_type: str) -> Dict[str, Any]:
    """Analyze patterns specific to project type."""
    if project_type == "web":
        return {
            "routing_patterns": "route" in code.lower(),
            "middleware_usage": "middleware" in code.lower(),
            "authentication": "auth" in code.lower()
        }
    elif project_type == "ml":
        return {
            "data_preprocessing": any(lib in code for lib in ["pandas", "numpy"]),
            "model_training": any(lib in code for lib in ["sklearn", "tensorflow", "pytorch"]),
            "feature_engineering": "feature" in code.lower()
        }
    else:
        return {"general_patterns": True}
