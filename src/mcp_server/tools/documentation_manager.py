"""
Documentation management and download system for Python versions.

This module provides comprehensive documentation management for all Python versions,
enabling the MCP server to have complete knowledge of Python features across versions.
"""

import asyncio
import os
import shutil
import traceback
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests

from ..config import TEMP_DIR
from ..utils.logging import log_tool_execution


# Python version documentation URLs
PYTHON_DOC_VERSIONS = {
    "3.15": {"status": "development", "url_base": "https://docs.python.org/3.15/"},
    "3.14": {"status": "pre-release", "url_base": "https://docs.python.org/3.14/"},
    "3.13": {"status": "stable", "url_base": "https://docs.python.org/3.13/"},
    "3.12": {"status": "security-fixes", "url_base": "https://docs.python.org/3.12/"},
    "3.11": {"status": "security-fixes", "url_base": "https://docs.python.org/3.11/"},
    "3.10": {"status": "security-fixes", "url_base": "https://docs.python.org/3.10/"},
    "3.9": {"status": "security-fixes", "url_base": "https://docs.python.org/3.9/"},
    "3.8": {"status": "EOL", "url_base": "https://docs.python.org/3.8/"},
    "3.7": {"status": "EOL", "url_base": "https://docs.python.org/3.7/"},
    "3.6": {"status": "EOL", "url_base": "https://docs.python.org/3.6/"},
    "3.5": {"status": "EOL", "url_base": "https://docs.python.org/3.5/"},
    "3.4": {"status": "EOL", "url_base": "https://docs.python.org/3.4/"},
    "3.3": {"status": "EOL", "url_base": "https://docs.python.org/3.3/"},
    "3.2": {"status": "EOL", "url_base": "https://docs.python.org/3.2/"},
    "3.1": {"status": "EOL", "url_base": "https://docs.python.org/3.1/"},
    "3.0": {"status": "EOL", "url_base": "https://docs.python.org/3.0/"},
    "2.7": {"status": "EOL", "url_base": "https://docs.python.org/2.7/"},
    "2.6": {"status": "EOL", "url_base": "https://docs.python.org/2.6/"},
}


@log_tool_execution("download_python_docs")
def download_python_documentation(
    versions: Optional[List[str]] = None,
    format_type: str = "html",
    docs_dir: str = "docs/python_manuals"
) -> Dict[str, Any]:
    """
    Download Python documentation for specified versions.
    
    Args:
        versions: List of Python versions to download (None for all)
        format_type: Documentation format (html, pdf, epub, text)
        docs_dir: Directory to store documentation
        
    Returns:
        Dict with download results and status
    """
    try:
        if versions is None:
            versions = list(PYTHON_DOC_VERSIONS.keys())
            
        # Create documentation directory
        docs_path = Path(docs_dir)
        docs_path.mkdir(parents=True, exist_ok=True)
        
        download_results = []
        total_size = 0
        
        for version in versions:
            if version not in PYTHON_DOC_VERSIONS:
                download_results.append({
                    "version": version,
                    "status": "error",
                    "error": f"Unknown Python version: {version}"
                })
                continue
                
            version_info = PYTHON_DOC_VERSIONS[version]
            
            # Create version directory
            version_dir = docs_path / f"python-{version}"
            version_dir.mkdir(exist_ok=True)
            
            # Download documentation
            try:
                download_url = construct_download_url(version, format_type)
                file_size = download_documentation_file(download_url, version_dir, version, format_type)
                
                download_results.append({
                    "version": version,
                    "status": "success",
                    "format": format_type,
                    "size_mb": file_size / (1024 * 1024),
                    "directory": str(version_dir),
                    "python_status": version_info["status"]
                })
                
                total_size += file_size
                
            except Exception as e:
                download_results.append({
                    "version": version,
                    "status": "error",
                    "error": str(e),
                    "python_status": version_info["status"]
                })
                
        # Generate documentation index
        index_file = create_documentation_index(docs_path, download_results)
        
        return {
            "status": "success",
            "result": {
                "downloaded_versions": len([r for r in download_results if r["status"] == "success"]),
                "failed_downloads": len([r for r in download_results if r["status"] == "error"]),
                "total_size_mb": total_size / (1024 * 1024),
                "format": format_type,
                "docs_directory": str(docs_path),
                "index_file": str(index_file),
                "download_details": download_results
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "download_python_docs"
        }


@log_tool_execution("search_python_docs")
def search_python_documentation(
    query: str,
    versions: Optional[List[str]] = None,
    docs_dir: str = "docs/python_manuals"
) -> Dict[str, Any]:
    """
    Search through downloaded Python documentation.
    
    Args:
        query: Search query
        versions: Python versions to search (None for all)
        docs_dir: Documentation directory
        
    Returns:
        Dict with search results
    """
    try:
        if not query:
            raise ValueError("query is required")
            
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            return {
                "status": "error",
                "error": "Documentation directory not found. Download documentation first.",
                "tool": "search_python_docs"
            }
            
        if versions is None:
            versions = list(PYTHON_DOC_VERSIONS.keys())
            
        search_results = []
        
        for version in versions:
            version_dir = docs_path / f"python-{version}"
            if not version_dir.exists():
                continue
                
            # Search in HTML files
            html_results = search_in_html_docs(version_dir, query, version)
            search_results.extend(html_results)
            
        # Sort results by relevance
        search_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Group results by version
        version_groups = {}
        for result in search_results:
            version = result["version"]
            if version not in version_groups:
                version_groups[version] = []
            version_groups[version].append(result)
            
        return {
            "status": "success",
            "result": {
                "query": query,
                "total_results": len(search_results),
                "searched_versions": len(version_groups),
                "results": search_results[:50],  # Top 50 results
                "results_by_version": version_groups
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "search_python_docs"
        }


@log_tool_execution("get_version_features")
def get_python_version_features(version: str) -> Dict[str, Any]:
    """
    Get detailed features and changes for a specific Python version.
    
    Args:
        version: Python version (e.g., "3.12")
        
    Returns:
        Dict with version features and changes
    """
    try:
        if version not in PYTHON_DOC_VERSIONS:
            raise ValueError(f"Unknown Python version: {version}")
            
        version_info = PYTHON_DOC_VERSIONS[version]
        
        # Define known features for each version
        version_features = get_known_version_features(version)
        
        # Get compatibility information
        compatibility = get_version_compatibility(version)
        
        # Get migration guidance
        migration_guide = get_migration_guidance(version)
        
        return {
            "status": "success",
            "result": {
                "version": version,
                "status": version_info["status"],
                "features": version_features,
                "compatibility": compatibility,
                "migration_guide": migration_guide,
                "documentation_url": version_info["url_base"]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "get_version_features"
        }


@log_tool_execution("compare_python_versions")
def compare_python_versions(version1: str, version2: str) -> Dict[str, Any]:
    """
    Compare features and changes between two Python versions.
    
    Args:
        version1: First Python version
        version2: Second Python version
        
    Returns:
        Dict with version comparison
    """
    try:
        if version1 not in PYTHON_DOC_VERSIONS:
            raise ValueError(f"Unknown Python version: {version1}")
        if version2 not in PYTHON_DOC_VERSIONS:
            raise ValueError(f"Unknown Python version: {version2}")
            
        features1 = get_known_version_features(version1)
        features2 = get_known_version_features(version2)
        
        # Find differences
        added_features = []
        removed_features = []
        changed_features = []
        
        all_feature_keys = set(features1.keys()) | set(features2.keys())
        
        for key in all_feature_keys:
            if key in features2 and key not in features1:
                added_features.append(key)
            elif key in features1 and key not in features2:
                removed_features.append(key)
            elif key in both and features1[key] != features2[key]:
                changed_features.append(key)
                
        # Determine upgrade/downgrade recommendations
        recommendations = generate_version_recommendations(version1, version2)
        
        return {
            "status": "success",
            "result": {
                "version1": version1,
                "version2": version2,
                "added_features": added_features,
                "removed_features": removed_features,
                "changed_features": changed_features,
                "recommendations": recommendations,
                "compatibility_notes": get_compatibility_notes(version1, version2)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "compare_python_versions"
        }


# Helper functions
def construct_download_url(version: str, format_type: str) -> str:
    """Construct download URL for Python documentation."""
    base_url = PYTHON_DOC_VERSIONS[version]["url_base"]
    
    format_mapping = {
        "html": f"archives/python-{version}-docs-html.zip",
        "pdf": f"archives/python-{version}-docs-pdf-a4.zip",
        "epub": f"archives/python-{version}-docs.epub",
        "text": f"archives/python-{version}-docs-text.zip"
    }
    
    if format_type not in format_mapping:
        raise ValueError(f"Unsupported format: {format_type}")
        
    return urljoin(base_url, format_mapping[format_type])


def download_documentation_file(url: str, target_dir: Path, version: str, format_type: str) -> int:
    """Download and extract documentation file."""
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    
    # Get file size
    file_size = int(response.headers.get('content-length', 0))
    
    # Download file
    filename = f"python-{version}-docs.{format_type}.zip" if format_type != "epub" else f"python-{version}-docs.epub"
    file_path = target_dir / filename
    
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                
    # Extract if it's a zip file
    if filename.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        # Remove the zip file after extraction
        file_path.unlink()
        
    return file_size


def create_documentation_index(docs_path: Path, download_results: List[Dict[str, Any]]) -> Path:
    """Create an index file for all downloaded documentation."""
    index_file = docs_path / "index.md"
    
    content = "# Python Documentation Index\n\n"
    content += "This directory contains Python documentation for multiple versions.\n\n"
    
    # Group by status
    status_groups = {}
    for result in download_results:
        if result["status"] == "success":
            status = result["python_status"]
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(result)
            
    # Write index
    for status, results in status_groups.items():
        content += f"## {status.title()} Versions\n\n"
        for result in sorted(results, key=lambda x: x["version"], reverse=True):
            content += f"- **Python {result['version']}** - {result['size_mb']:.1f}MB - [{result['directory']}]({result['directory']})\n"
        content += "\n"
        
    # Add search instructions
    content += """
## How to Use

1. **Search Documentation**: Use the search_python_documentation tool to find specific topics
2. **Compare Versions**: Use compare_python_versions to see differences between versions
3. **Get Features**: Use get_python_version_features to get detailed version information

## Directory Structure

Each version directory contains:
- HTML documentation (if downloaded in HTML format)
- PDF documentation (if downloaded in PDF format)
- EPUB documentation (if downloaded in EPUB format)
"""
    
    index_file.write_text(content)
    return index_file


def search_in_html_docs(version_dir: Path, query: str, version: str) -> List[Dict[str, Any]]:
    """Search for query in HTML documentation files."""
    results = []
    query_lower = query.lower()
    
    # Search in HTML files
    for html_file in version_dir.rglob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            if query_lower in content_lower:
                # Extract context around the match
                lines = content.split('\n')
                matching_lines = []
                
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # Get context (5 lines before and after)
                        start = max(0, i - 5)
                        end = min(len(lines), i + 6)
                        context = '\n'.join(lines[start:end])
                        matching_lines.append({
                            "line_number": i + 1,
                            "context": context,
                            "line_content": line.strip()
                        })
                        
                if matching_lines:
                    # Calculate relevance score
                    relevance_score = calculate_relevance_score(content_lower, query_lower)
                    
                    results.append({
                        "version": version,
                        "file": str(html_file.relative_to(version_dir)),
                        "matches": len(matching_lines),
                        "relevance_score": relevance_score,
                        "matching_lines": matching_lines[:5],  # Top 5 matches
                        "file_size": html_file.stat().st_size
                    })
                    
        except Exception:
            # Skip files that can't be read
            continue
            
    return results


def calculate_relevance_score(content: str, query: str) -> float:
    """Calculate relevance score for search results."""
    query_count = content.count(query)
    content_length = len(content)
    
    # Base score on frequency and content length
    if content_length == 0:
        return 0
        
    frequency_score = query_count / content_length * 1000
    
    # Boost score for title matches
    if f"<title>{query}" in content or f"<h1>{query}" in content:
        frequency_score *= 2
        
    return frequency_score


def get_known_version_features(version: str) -> Dict[str, Any]:
    """Get known features for a Python version."""
    features = {
        "3.13": {
            "free_threaded_python": "Experimental free-threaded build",
            "interactive_interpreter": "Improved interactive interpreter",
            "type_system": "Type system improvements",
            "performance": "General performance improvements"
        },
        "3.12": {
            "f_string_debugging": "Enhanced f-string debugging",
            "type_hints": "Improved type hints support",
            "pathlib": "pathlib.Path improvements",
            "performance": "25% performance improvement over 3.11"
        },
        "3.11": {
            "exception_groups": "Exception Groups and except* syntax",
            "tomllib": "TOML parsing support in standard library",
            "async_task_groups": "Async Task Groups",
            "performance": "10-60% performance improvement"
        },
        "3.10": {
            "match_statements": "Structural Pattern Matching (match/case)",
            "union_types": "Union types with | operator",
            "parameter_specification": "Parameter specification variables",
            "precise_error_messages": "Better error messages"
        },
        "3.9": {
            "dict_union": "Dictionary union operators (| and |=)",
            "type_hinting": "Generic types without typing module",
            "string_methods": "removeprefix() and removesuffix()",
            "decorator_any_expression": "Decorators can use any expression"
        },
        "3.8": {
            "walrus_operator": "Assignment expressions (:=)",
            "positional_only": "Positional-only parameters",
            "f_string_debugging": "f-string = debugging",
            "typing_final": "typing.Final and @final"
        }
    }
    
    return features.get(version, {})


def get_version_compatibility(version: str) -> Dict[str, Any]:
    """Get compatibility information for a version."""
    compatibility = {
        "backwards_compatible": True,
        "breaking_changes": [],
        "deprecated_features": [],
        "minimum_requirements": {}
    }
    
    # Version-specific compatibility notes
    if version >= "3.12":
        compatibility["minimum_requirements"]["python"] = ">=3.8"
        compatibility["deprecated_features"].append("distutils module")
        
    if version >= "3.10":
        compatibility["deprecated_features"].extend(["asyncore", "asynchat"])
        
    if version >= "3.9":
        compatibility["breaking_changes"].append("Changed behavior of list.sort() and sorted()")
        
    return compatibility


def get_migration_guidance(version: str) -> List[Dict[str, str]]:
    """Get migration guidance for a version."""
    guidance = []
    
    if version >= "3.10":
        guidance.append({
            "from": "if/elif chains",
            "to": "match/case statements",
            "reason": "Better readability and performance"
        })
        guidance.append({
            "from": "Union[str, int]",
            "to": "str | int",
            "reason": "Cleaner type hint syntax"
        })
        
    if version >= "3.9":
        guidance.append({
            "from": "Dict[str, int]",
            "to": "dict[str, int]",
            "reason": "Built-in generics don't need typing import"
        })
        
    if version >= "3.8":
        guidance.append({
            "from": "if (n := len(items)) > 0:",
            "to": "Use walrus operator for assignment expressions",
            "reason": "More concise code"
        })
        
    return guidance


def generate_version_recommendations(version1: str, version2: str) -> List[Dict[str, str]]:
    """Generate recommendations for version upgrade/downgrade."""
    recommendations = []
    
    v1_major, v1_minor = map(int, version1.split('.'))
    v2_major, v2_minor = map(int, version2.split('.'))
    
    if (v2_major, v2_minor) > (v1_major, v1_minor):
        recommendations.append({
            "type": "upgrade",
            "action": f"Upgrade from {version1} to {version2}",
            "benefits": "Access to new features and performance improvements",
            "considerations": "Test compatibility with existing code"
        })
    elif (v2_major, v2_minor) < (v1_major, v1_minor):
        recommendations.append({
            "type": "downgrade",
            "action": f"Downgrade from {version1} to {version2}",
            "benefits": "Better compatibility with legacy systems",
            "considerations": "Loss of newer features and performance improvements"
        })
    else:
        recommendations.append({
            "type": "no_change",
            "action": "Versions are the same",
            "benefits": "No action needed",
            "considerations": "Consider upgrading to latest stable version"
        })
        
    return recommendations


def get_compatibility_notes(version1: str, version2: str) -> List[str]:
    """Get compatibility notes between versions."""
    notes = []
    
    v1_parts = tuple(map(int, version1.split('.')))
    v2_parts = tuple(map(int, version2.split('.')))
    
    if v1_parts[0] != v2_parts[0]:
        notes.append("Major version change - expect significant breaking changes")
    elif v1_parts[1] != v2_parts[1]:
        notes.append("Minor version change - new features available, minimal breaking changes")
    else:
        notes.append("Patch version change - bug fixes and security updates only")
        
    # Specific version notes
    if "3.10" in [version1, version2] and "3.9" in [version1, version2]:
        notes.append("Match statements and | union syntax introduced in 3.10")
        
    if "3.9" in [version1, version2] and "3.8" in [version1, version2]:
        notes.append("Dictionary union operators and generic types introduced in 3.9")
        
    if "3.8" in [version1, version2] and "3.7" in [version1, version2]:
        notes.append("Walrus operator and positional-only parameters introduced in 3.8")
        
    return notes
