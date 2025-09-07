"""
Performance profiling and optimization tools for Python code.

This module provides comprehensive performance analysis, profiling,
and optimization suggestions for Python code.
"""

import ast
import cProfile
import io
import pstats
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("profile_performance")
def profile_code_performance(code: str, sort_by: str = "cumulative") -> Dict[str, Any]:
    """
    Profile Python code performance using cProfile.
    
    Args:
        code: Python code to profile
        sort_by: Sort criterion (cumulative, time, calls, name)
        
    Returns:
        Dict with profiling results and optimization suggestions
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Validate code safety
        safety_check = validate_code_safety(code)
        if not safety_check["is_safe"]:
            raise ValueError(f"Code safety violation: {safety_check['reason']}")
            
        # Create profiler
        profiler = cProfile.Profile()
        
        # Prepare execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'time': time,
            'range': range,
            'len': len,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
        }
        
        # Profile the code execution
        start_time = time.perf_counter()
        profiler.enable()
        
        try:
            exec(code, exec_globals)
        except Exception as e:
            profiler.disable()
            return {
                "status": "error",
                "error": f"Execution error: {str(e)}",
                "tool": "profile_performance"
            }
            
        profiler.disable()
        end_time = time.perf_counter()
        
        # Get profiling statistics
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats(sort_by)
        stats.print_stats(50)  # Top 50 functions
        
        profile_output = stats_stream.getvalue()
        
        # Parse statistics for structured data
        parsed_stats = parse_profile_stats(stats)
        
        # Generate optimization suggestions
        suggestions = generate_performance_suggestions(parsed_stats, code)
        
        # Calculate performance metrics
        metrics = calculate_performance_metrics(parsed_stats, end_time - start_time)
        
        return {
            "status": "success",
            "result": {
                "execution_time": end_time - start_time,
                "profile_output": profile_output,
                "top_functions": parsed_stats[:10],
                "performance_metrics": metrics,
                "optimization_suggestions": suggestions,
                "sort_by": sort_by
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "profile_performance"
        }


@log_tool_execution("memory_profile")
def profile_memory_usage(code: str) -> Dict[str, Any]:
    """
    Profile memory usage of Python code.
    
    Args:
        code: Python code to profile
        
    Returns:
        Dict with memory profiling results
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        # Validate code safety
        safety_check = validate_code_safety(code)
        if not safety_check["is_safe"]:
            raise ValueError(f"Code safety violation: {safety_check['reason']}")
            
        try:
            import psutil
            import gc
        except ImportError:
            return {
                "status": "error",
                "error": "psutil not installed. Install with: pip install psutil",
                "tool": "memory_profile"
            }
            
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Force garbage collection
        gc.collect()
        
        # Execute code and monitor memory
        exec_globals = {
            '__builtins__': __builtins__,
            'gc': gc,
            'psutil': psutil
        }
        
        try:
            exec(code, exec_globals)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Execution error: {str(e)}",
                "tool": "memory_profile"
            }
            
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = final_memory - initial_memory
        
        # Get garbage collection stats
        gc_stats = gc.get_stats()
        
        # Generate memory optimization suggestions
        suggestions = generate_memory_suggestions(memory_delta, code)
        
        return {
            "status": "success",
            "result": {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_delta_mb": memory_delta,
                "gc_stats": gc_stats,
                "memory_suggestions": suggestions,
                "memory_efficiency": calculate_memory_efficiency(memory_delta)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "memory_profile"
        }


@log_tool_execution("benchmark_code")
def benchmark_code_variants(code_variants: List[str], iterations: int = 1000) -> Dict[str, Any]:
    """
    Benchmark multiple code variants to find the fastest implementation.
    
    Args:
        code_variants: List of code strings to benchmark
        iterations: Number of iterations to run each variant
        
    Returns:
        Dict with benchmark results and fastest implementation
    """
    try:
        if not code_variants:
            raise ValueError("code_variants is required")
            
        if iterations > 10000:
            iterations = 10000  # Safety limit
            
        results = []
        
        for i, code in enumerate(code_variants):
            # Validate code safety
            safety_check = validate_code_safety(code)
            if not safety_check["is_safe"]:
                results.append({
                    "variant": i + 1,
                    "error": f"Code safety violation: {safety_check['reason']}",
                    "execution_time": float('inf')
                })
                continue
                
            # Prepare execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'time': time,
                'range': range,
                'len': len,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
            }
            
            # Benchmark the code
            times = []
            error_occurred = False
            
            for _ in range(iterations):
                start_time = time.perf_counter()
                try:
                    exec(code, exec_globals.copy())
                except Exception as e:
                    error_occurred = True
                    break
                end_time = time.perf_counter()
                times.append(end_time - start_time)
                
            if error_occurred:
                results.append({
                    "variant": i + 1,
                    "error": "Execution error during benchmarking",
                    "execution_time": float('inf')
                })
            else:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results.append({
                    "variant": i + 1,
                    "average_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "total_time": sum(times),
                    "iterations": iterations,
                    "code_preview": code[:100] + "..." if len(code) > 100 else code
                })
                
        # Find fastest variant
        valid_results = [r for r in results if "error" not in r]
        fastest_variant = min(valid_results, key=lambda x: x["average_time"]) if valid_results else None
        
        # Generate performance comparison
        comparison = generate_performance_comparison(results)
        
        return {
            "status": "success",
            "result": {
                "benchmark_results": results,
                "fastest_variant": fastest_variant,
                "performance_comparison": comparison,
                "iterations": iterations,
                "total_variants": len(code_variants)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "benchmark_code"
        }


@log_tool_execution("optimize_performance")
def suggest_performance_optimizations(code: str) -> Dict[str, Any]:
    """
    Analyze code and suggest performance optimizations.
    
    Args:
        code: Python code to analyze
        
    Returns:
        Dict with optimization suggestions and improved code
    """
    try:
        if not code:
            raise ValueError("code is required")
            
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "status": "error",
                "error": f"Syntax error: {e}",
                "tool": "optimize_performance"
            }
            
        optimizations = []
        
        # Detect performance anti-patterns
        optimizations.extend(detect_loop_optimizations(tree, code))
        optimizations.extend(detect_data_structure_optimizations(tree, code))
        optimizations.extend(detect_function_call_optimizations(tree, code))
        optimizations.extend(detect_string_optimizations(code))
        optimizations.extend(detect_import_optimizations(tree, code))
        
        # Generate optimized code suggestions
        optimized_code = apply_basic_optimizations(code)
        
        # Calculate optimization impact
        impact_score = calculate_optimization_impact(optimizations)
        
        return {
            "status": "success",
            "result": {
                "original_code": code,
                "optimizations": optimizations,
                "optimized_code": optimized_code,
                "optimization_impact": impact_score,
                "total_suggestions": len(optimizations)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "optimize_performance"
        }


# Helper functions
def parse_profile_stats(stats: pstats.Stats) -> List[Dict[str, Any]]:
    """Parse cProfile statistics into structured data."""
    parsed_stats = []
    
    for func_info, (calls, non_recursive_calls, total_time, cumulative_time) in stats.stats.items():
        filename, line_number, function_name = func_info
        
        parsed_stats.append({
            "function": function_name,
            "filename": filename,
            "line_number": line_number,
            "calls": calls,
            "non_recursive_calls": non_recursive_calls,
            "total_time": total_time,
            "cumulative_time": cumulative_time,
            "time_per_call": total_time / calls if calls > 0 else 0
        })
        
    # Sort by cumulative time
    parsed_stats.sort(key=lambda x: x["cumulative_time"], reverse=True)
    return parsed_stats


def generate_performance_suggestions(stats: List[Dict[str, Any]], code: str) -> List[Dict[str, Any]]:
    """Generate performance optimization suggestions based on profiling."""
    suggestions = []
    
    if not stats:
        return suggestions
        
    # Check for expensive functions
    top_function = stats[0]
    if top_function["cumulative_time"] > 0.1:  # More than 0.1 seconds
        suggestions.append({
            "type": "expensive_function",
            "function": top_function["function"],
            "time": top_function["cumulative_time"],
            "suggestion": f"Function '{top_function['function']}' takes {top_function['cumulative_time']:.3f}s. Consider optimization.",
            "priority": "high"
        })
        
    # Check for excessive function calls
    high_call_functions = [s for s in stats if s["calls"] > 1000]
    for func in high_call_functions:
        suggestions.append({
            "type": "excessive_calls",
            "function": func["function"],
            "calls": func["calls"],
            "suggestion": f"Function '{func['function']}' called {func['calls']} times. Consider caching or optimization.",
            "priority": "medium"
        })
        
    return suggestions


def calculate_performance_metrics(stats: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
    """Calculate performance metrics from profiling data."""
    if not stats:
        return {"total_functions": 0, "total_calls": 0, "average_time_per_call": 0}
        
    total_calls = sum(s["calls"] for s in stats)
    total_function_time = sum(s["total_time"] for s in stats)
    
    return {
        "total_execution_time": total_time,
        "total_functions": len(stats),
        "total_calls": total_calls,
        "total_function_time": total_function_time,
        "average_time_per_call": total_function_time / total_calls if total_calls > 0 else 0,
        "overhead_percentage": ((total_time - total_function_time) / total_time * 100) if total_time > 0 else 0
    }


def generate_memory_suggestions(memory_delta: float, code: str) -> List[Dict[str, Any]]:
    """Generate memory optimization suggestions."""
    suggestions = []
    
    if memory_delta > 100:  # More than 100MB
        suggestions.append({
            "type": "high_memory_usage",
            "memory_mb": memory_delta,
            "suggestion": f"Code uses {memory_delta:.2f}MB of memory. Consider memory optimization.",
            "priority": "high"
        })
        
    # Check for potential memory leaks
    if "while True:" in code and "break" not in code:
        suggestions.append({
            "type": "potential_memory_leak",
            "suggestion": "Infinite loop detected. Ensure proper memory cleanup.",
            "priority": "critical"
        })
        
    # Check for large data structures
    if "list(" in code and "range(" in code:
        suggestions.append({
            "type": "large_list_creation",
            "suggestion": "Consider using generators instead of creating large lists.",
            "priority": "medium"
        })
        
    return suggestions


def calculate_memory_efficiency(memory_delta: float) -> str:
    """Calculate memory efficiency rating."""
    if memory_delta < 1:
        return "excellent"
    elif memory_delta < 10:
        return "good"
    elif memory_delta < 50:
        return "fair"
    elif memory_delta < 100:
        return "poor"
    else:
        return "very_poor"


def generate_performance_comparison(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate performance comparison between variants."""
    valid_results = [r for r in results if "error" not in r]
    
    if len(valid_results) < 2:
        return {"comparison": "insufficient_data"}
        
    fastest = min(valid_results, key=lambda x: x["average_time"])
    slowest = max(valid_results, key=lambda x: x["average_time"])
    
    speedup = slowest["average_time"] / fastest["average_time"]
    
    return {
        "fastest_variant": fastest["variant"],
        "slowest_variant": slowest["variant"],
        "speedup_factor": speedup,
        "performance_difference_percent": ((slowest["average_time"] - fastest["average_time"]) / fastest["average_time"]) * 100
    }


def detect_loop_optimizations(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect loop optimization opportunities."""
    optimizations = []
    
    # Check for range(len()) pattern
    if "range(len(" in code:
        optimizations.append({
            "type": "loop_optimization",
            "pattern": "range(len())",
            "suggestion": "Use enumerate() instead of range(len()) for better performance",
            "priority": "medium",
            "example": "for i, item in enumerate(items) instead of for i in range(len(items))"
        })
        
    # Check for list.append() in loops
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Call) and 
                    isinstance(stmt.func, ast.Attribute) and 
                    stmt.func.attr == "append"):
                    optimizations.append({
                        "type": "list_comprehension",
                        "pattern": "append in loop",
                        "suggestion": "Consider using list comprehension for better performance",
                        "priority": "medium"
                    })
                    break
                    
    return optimizations


def detect_data_structure_optimizations(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect data structure optimization opportunities."""
    optimizations = []
    
    # Check for membership testing in lists
    if " in [" in code:
        optimizations.append({
            "type": "data_structure",
            "pattern": "membership testing in list",
            "suggestion": "Use set for membership testing (O(1) vs O(n))",
            "priority": "high",
            "example": "Use 'item in {1, 2, 3}' instead of 'item in [1, 2, 3]'"
        })
        
    # Check for dictionary.keys() iterations
    if ".keys()" in code:
        optimizations.append({
            "type": "dictionary_iteration",
            "pattern": "dict.keys() iteration",
            "suggestion": "Iterate directly over dictionary for better performance",
            "priority": "low",
            "example": "Use 'for key in dict' instead of 'for key in dict.keys()'"
        })
        
    return optimizations


def detect_function_call_optimizations(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect function call optimization opportunities."""
    optimizations = []
    
    # Check for repeated function calls
    function_calls = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            function_calls[func_name] = function_calls.get(func_name, 0) + 1
            
    for func_name, count in function_calls.items():
        if count > 10:  # Called more than 10 times
            optimizations.append({
                "type": "function_caching",
                "function": func_name,
                "calls": count,
                "suggestion": f"Function '{func_name}' called {count} times. Consider caching results.",
                "priority": "medium"
            })
            
    return optimizations


def detect_string_optimizations(code: str) -> List[Dict[str, Any]]:
    """Detect string optimization opportunities."""
    optimizations = []
    
    # Check for string concatenation in loops
    if "+=" in code and ("for " in code or "while " in code):
        optimizations.append({
            "type": "string_concatenation",
            "pattern": "string += in loop",
            "suggestion": "Use list.join() or f-strings for string concatenation in loops",
            "priority": "high",
            "example": "''.join(string_list) instead of repeated +="
        })
        
    # Check for old-style string formatting
    if "%" in code and "(" in code:
        optimizations.append({
            "type": "string_formatting",
            "pattern": "old-style % formatting",
            "suggestion": "Use f-strings for better performance and readability",
            "priority": "medium",
            "example": "f'{variable}' instead of '%s' % variable"
        })
        
    return optimizations


def detect_import_optimizations(tree: ast.AST, code: str) -> List[Dict[str, Any]]:
    """Detect import optimization opportunities."""
    optimizations = []
    
    # Check for imports inside functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    optimizations.append({
                        "type": "import_location",
                        "function": node.name,
                        "suggestion": f"Move import out of function '{node.name}' to module level",
                        "priority": "low"
                    })
                    
    return optimizations


def apply_basic_optimizations(code: str) -> str:
    """Apply basic optimizations to code."""
    optimized = code
    
    # Convert range(len()) to enumerate()
    import re
    pattern = r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):'
    replacement = r'for \1, _ in enumerate(\2):'
    optimized = re.sub(pattern, replacement, optimized)
    
    # Convert % formatting to f-strings (simplified)
    pattern = r'(["\'])([^"\']*?)%s([^"\']*?)\1\s*%\s*\(([^)]+)\)'
    matches = re.findall(pattern, optimized)
    for quote, before, after, var in matches:
        old = f'{quote}{before}%s{after}{quote} % ({var})'
        new = f'f{quote}{before}{{{var.strip()}}}{after}{quote}'
        optimized = optimized.replace(old, new)
        
    return optimized


def calculate_optimization_impact(optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate the potential impact of optimizations."""
    if not optimizations:
        return {"impact_score": 0, "potential_speedup": "none"}
        
    priority_weights = {"low": 1, "medium": 3, "high": 5, "critical": 10}
    total_impact = sum(priority_weights.get(opt.get("priority", "low"), 1) for opt in optimizations)
    
    impact_score = min(total_impact, 100)  # Cap at 100
    
    if impact_score < 10:
        potential_speedup = "minimal"
    elif impact_score < 30:
        potential_speedup = "moderate"
    elif impact_score < 60:
        potential_speedup = "significant"
    else:
        potential_speedup = "substantial"
        
    return {
        "impact_score": impact_score,
        "potential_speedup": potential_speedup,
        "high_priority_optimizations": len([o for o in optimizations if o.get("priority") in ["high", "critical"]])
    }
