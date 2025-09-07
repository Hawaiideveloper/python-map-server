"""
Advanced Git and Version Control System integration tools.

This module provides expert-level VCS integration including Git workflows,
code review automation, and repository analysis that a 30-year veteran would use.
"""

import os
import re
import subprocess
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logging import log_tool_execution


@log_tool_execution("analyze_git_repository")
def analyze_git_repository(repo_path: str = ".") -> Dict[str, Any]:
    """
    Perform comprehensive Git repository analysis.
    
    Args:
        repo_path: Path to Git repository
        
    Returns:
        Dict with repository analysis and expert insights
    """
    try:
        if not is_git_repository(repo_path):
            return {
                "status": "error",
                "error": "Not a Git repository",
                "suggestion": "Initialize with 'git init' or check the path"
            }
            
        # Repository analysis
        analysis = {
            "repository_health": analyze_repository_health(repo_path),
            "branch_analysis": analyze_branches(repo_path),
            "commit_analysis": analyze_commits(repo_path),
            "contributor_analysis": analyze_contributors(repo_path),
            "file_analysis": analyze_file_patterns(repo_path),
            "workflow_analysis": analyze_git_workflow(repo_path),
            "security_analysis": analyze_repository_security(repo_path),
            "best_practices": check_git_best_practices(repo_path)
        }
        
        # Generate expert recommendations
        recommendations = generate_git_recommendations(analysis)
        
        # Calculate repository score
        repo_score = calculate_repository_score(analysis)
        
        return {
            "status": "success",
            "result": {
                **analysis,
                "repository_score": repo_score,
                "expert_recommendations": recommendations,
                "quick_wins": identify_quick_wins(analysis)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "analyze_git_repository"
        }


@log_tool_execution("suggest_git_workflow")
def suggest_git_workflow(project_type: str = "general", team_size: int = 1) -> Dict[str, Any]:
    """
    Suggest optimal Git workflow based on project and team characteristics.
    
    Args:
        project_type: Type of project (web, library, enterprise, open-source)
        team_size: Number of team members
        
    Returns:
        Dict with workflow recommendations and implementation guide
    """
    try:
        # Determine appropriate workflow
        workflow = determine_optimal_workflow(project_type, team_size)
        
        # Generate workflow implementation
        implementation = generate_workflow_implementation(workflow, project_type, team_size)
        
        # Create branch strategy
        branch_strategy = create_branch_strategy(workflow, project_type)
        
        # Generate automation recommendations
        automation = suggest_workflow_automation(workflow, project_type)
        
        return {
            "status": "success",
            "result": {
                "recommended_workflow": workflow,
                "implementation_guide": implementation,
                "branch_strategy": branch_strategy,
                "automation_suggestions": automation,
                "expert_tips": get_workflow_expert_tips(workflow, team_size)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "suggest_git_workflow"
        }


@log_tool_execution("generate_git_hooks")
def generate_git_hooks(hook_types: List[str]) -> Dict[str, Any]:
    """
    Generate Git hooks for code quality and automation.
    
    Args:
        hook_types: Types of hooks to generate (pre-commit, pre-push, post-commit, etc.)
        
    Returns:
        Dict with generated Git hooks and installation instructions
    """
    try:
        hooks = {}
        
        for hook_type in hook_types:
            if hook_type in GIT_HOOK_TEMPLATES:
                hooks[hook_type] = {
                    "script": GIT_HOOK_TEMPLATES[hook_type]["script"],
                    "purpose": GIT_HOOK_TEMPLATES[hook_type]["purpose"],
                    "installation": f"Save to .git/hooks/{hook_type} and chmod +x",
                    "requirements": GIT_HOOK_TEMPLATES[hook_type].get("requirements", [])
                }
        
        # Generate hook installation script
        installation_script = generate_hook_installation_script(hooks)
        
        # Suggest additional tooling
        tooling_suggestions = suggest_hook_tooling()
        
        return {
            "status": "success",
            "result": {
                "hooks": hooks,
                "installation_script": installation_script,
                "tooling_suggestions": tooling_suggestions,
                "expert_guidance": get_git_hooks_guidance()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "generate_git_hooks"
        }


@log_tool_execution("analyze_code_changes")
def analyze_code_changes(since_ref: str = "HEAD~10") -> Dict[str, Any]:
    """
    Analyze code changes and suggest review focus areas.
    
    Args:
        since_ref: Git reference to compare against (default: last 10 commits)
        
    Returns:
        Dict with change analysis and review recommendations
    """
    try:
        # Get changed files
        changed_files = get_changed_files(since_ref)
        
        # Analyze change patterns
        change_analysis = analyze_change_patterns(changed_files, since_ref)
        
        # Identify review focus areas
        review_focus = identify_review_focus_areas(change_analysis)
        
        # Generate code review checklist
        review_checklist = generate_code_review_checklist(change_analysis)
        
        # Risk assessment
        risk_assessment = assess_change_risk(change_analysis)
        
        return {
            "status": "success",
            "result": {
                "changed_files": changed_files,
                "change_analysis": change_analysis,
                "review_focus_areas": review_focus,
                "review_checklist": review_checklist,
                "risk_assessment": risk_assessment,
                "expert_review_tips": get_code_review_expert_tips()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "analyze_code_changes"
        }


@log_tool_execution("git_bisect_helper")
def suggest_git_bisect_strategy(error_description: str, last_known_good: str = "") -> Dict[str, Any]:
    """
    Suggest Git bisect strategy for finding problematic commits.
    
    Args:
        error_description: Description of the error or issue
        last_known_good: Last known good commit (optional)
        
    Returns:
        Dict with bisect strategy and commands
    """
    try:
        # Analyze error description for bisect strategy
        bisect_strategy = analyze_bisect_strategy(error_description)
        
        # Generate bisect commands
        bisect_commands = generate_bisect_commands(last_known_good, bisect_strategy)
        
        # Create test script suggestions
        test_script = suggest_bisect_test_script(error_description)
        
        # Provide bisect guidance
        guidance = get_bisect_expert_guidance(error_description)
        
        return {
            "status": "success",
            "result": {
                "bisect_strategy": bisect_strategy,
                "commands": bisect_commands,
                "test_script_suggestion": test_script,
                "expert_guidance": guidance,
                "estimated_commits": estimate_bisect_commits()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "git_bisect_helper"
        }


# Git hook templates
GIT_HOOK_TEMPLATES = {
    "pre-commit": {
        "purpose": "Validate code quality before commit",
        "script": """#!/bin/bash
# Pre-commit hook for code quality

set -e

echo "Running pre-commit checks..."

# Check for Python syntax errors
if find . -name "*.py" | head -1 | grep -q .; then
    echo "Checking Python syntax..."
    python -m py_compile $(find . -name "*.py" | grep -v __pycache__)
fi

# Run linting
if command -v ruff &> /dev/null; then
    echo "Running ruff linter..."
    ruff check .
fi

# Run type checking
if command -v mypy &> /dev/null; then
    echo "Running mypy type checking..."
    mypy . --ignore-missing-imports
fi

# Check for large files
echo "Checking for large files..."
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 1048576 ]; then  # 1MB
            echo "Error: $file is larger than 1MB ($size bytes)"
            exit 1
        fi
    fi
done

# Check for secrets
echo "Checking for potential secrets..."
if git diff --cached | grep -E "(password|secret|key|token).*=" | grep -v "# noqa"; then
    echo "Error: Potential secrets found in staged changes"
    echo "Use '# noqa' comment to bypass if intentional"
    exit 1
fi

echo "Pre-commit checks passed!"
""",
        "requirements": ["ruff", "mypy"]
    },
    
    "pre-push": {
        "purpose": "Run comprehensive tests before pushing",
        "script": """#!/bin/bash
# Pre-push hook for comprehensive testing

set -e

echo "Running pre-push checks..."

# Run tests
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    echo "Running pytest..."
    python -m pytest
elif [ -f "tests" ]; then
    echo "Running unittest..."
    python -m unittest discover tests
fi

# Check test coverage
if command -v coverage &> /dev/null; then
    echo "Checking test coverage..."
    coverage run -m pytest
    coverage report --fail-under=80
fi

# Security scan
if command -v bandit &> /dev/null; then
    echo "Running security scan..."
    bandit -r . -f json | python -c "
import sys, json
data = json.load(sys.stdin)
if data['results']:
    print('Security issues found!')
    sys.exit(1)
print('Security scan passed!')
"
fi

echo "Pre-push checks passed!"
""",
        "requirements": ["pytest", "coverage", "bandit"]
    },
    
    "commit-msg": {
        "purpose": "Validate commit message format",
        "script": """#!/bin/bash
# Commit message validation hook

commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    echo "Format: type(scope): description"
    echo "Types: feat, fix, docs, style, refactor, test, chore"
    echo "Example: feat(auth): add user authentication"
    exit 1
fi

# Check for imperative mood
first_line=$(head -n1 "$1")
description=$(echo "$first_line" | sed 's/^[^:]*: //')

if echo "$description" | grep -qE "^(added|fixed|updated|changed)"; then
    echo "Use imperative mood in commit messages!"
    echo "Use 'add' instead of 'added', 'fix' instead of 'fixed', etc."
    exit 1
fi

echo "Commit message format is valid!"
""",
        "requirements": []
    },
    
    "post-commit": {
        "purpose": "Post-commit automation and notifications",
        "script": """#!/bin/bash
# Post-commit hook for automation

# Update documentation if docs changed
if git diff HEAD~1 --name-only | grep -q "docs/\\|README\\|*.md"; then
    echo "Documentation changed, consider updating..."
fi

# Notify about important changes
if git diff HEAD~1 --name-only | grep -q "requirements\\|setup\\|pyproject"; then
    echo "Dependencies changed! Run: pip install -r requirements.txt"
fi

# Auto-tag releases
if git log -1 --pretty=%B | grep -q "^release:"; then
    version=$(git log -1 --pretty=%B | grep -o "v[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+")
    if [ -n "$version" ]; then
        git tag "$version"
        echo "Created tag: $version"
    fi
fi
""",
        "requirements": []
    }
}


# Helper functions
def is_git_repository(path: str) -> bool:
    """Check if path is a Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def analyze_repository_health(repo_path: str) -> Dict[str, Any]:
    """Analyze overall repository health."""
    health = {}
    
    try:
        # Check for common files
        important_files = [".gitignore", "README.md", "LICENSE", "requirements.txt", "pyproject.toml"]
        present_files = []
        missing_files = []
        
        for file in important_files:
            if os.path.exists(os.path.join(repo_path, file)):
                present_files.append(file)
            else:
                missing_files.append(file)
        
        health["important_files"] = {
            "present": present_files,
            "missing": missing_files,
            "score": len(present_files) / len(important_files) * 100
        }
        
        # Check repository size
        result = subprocess.run(
            ["git", "count-objects", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            size_info = {}
            for line in result.stdout.split('\n'):
                if ' ' in line:
                    key, value = line.split(' ', 1)
                    size_info[key] = value
            health["repository_size"] = size_info
        
        # Check for large files
        large_files = find_large_files(repo_path)
        health["large_files"] = large_files
        
    except Exception as e:
        health["error"] = str(e)
    
    return health


def analyze_branches(repo_path: str) -> Dict[str, Any]:
    """Analyze branch structure and strategy."""
    try:
        # Get all branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": "Could not retrieve branch information"}
        
        branches = []
        current_branch = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line:
                if line.startswith('*'):
                    current_branch = line[2:]
                    branches.append(line[2:])
                elif not line.startswith('remotes/origin/HEAD'):
                    branches.append(line)
        
        # Analyze branch patterns
        branch_patterns = analyze_branch_patterns(branches)
        
        # Check for stale branches
        stale_branches = find_stale_branches(repo_path)
        
        return {
            "total_branches": len(branches),
            "current_branch": current_branch,
            "branch_patterns": branch_patterns,
            "stale_branches": stale_branches,
            "branch_strategy": infer_branch_strategy(branches)
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_commits(repo_path: str) -> Dict[str, Any]:
    """Analyze commit history and patterns."""
    try:
        # Get commit statistics
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='3 months ago'"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": "Could not retrieve commit history"}
        
        commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Analyze commit messages
        commit_analysis = analyze_commit_messages(commits)
        
        # Get commit frequency
        frequency = analyze_commit_frequency(repo_path)
        
        return {
            "recent_commits": len(commits),
            "commit_message_analysis": commit_analysis,
            "commit_frequency": frequency,
            "commit_quality_score": calculate_commit_quality_score(commit_analysis)
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_contributors(repo_path: str) -> Dict[str, Any]:
    """Analyze contributor patterns."""
    try:
        # Get contributor statistics
        result = subprocess.run(
            ["git", "shortlog", "-sn", "--since='6 months ago'"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": "Could not retrieve contributor information"}
        
        contributors = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    contributors.append({
                        "commits": int(parts[0]),
                        "name": parts[1]
                    })
        
        return {
            "active_contributors": len(contributors),
            "top_contributors": contributors[:5],
            "contribution_distribution": analyze_contribution_distribution(contributors)
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_file_patterns(repo_path: str) -> Dict[str, Any]:
    """Analyze file patterns and organization."""
    try:
        # Get file statistics
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": "Could not retrieve file list"}
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Analyze file types
        file_types = {}
        for file in files:
            ext = os.path.splitext(file)[1]
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Check for Python project structure
        python_structure = analyze_python_structure(files)
        
        return {
            "total_files": len(files),
            "file_types": file_types,
            "python_project_structure": python_structure,
            "organization_score": calculate_organization_score(files)
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_git_workflow(repo_path: str) -> Dict[str, Any]:
    """Analyze Git workflow patterns."""
    try:
        # Check for merge vs rebase patterns
        result = subprocess.run(
            ["git", "log", "--merges", "--oneline", "--since='3 months ago'"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        merge_commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Check for feature branch patterns
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='3 months ago'"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        total_commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Analyze workflow type
        workflow_type = infer_workflow_type(merge_commits, total_commits)
        
        return {
            "merge_commits": merge_commits,
            "total_commits": total_commits,
            "merge_ratio": merge_commits / total_commits if total_commits > 0 else 0,
            "inferred_workflow": workflow_type,
            "workflow_health": assess_workflow_health(merge_commits, total_commits)
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_repository_security(repo_path: str) -> Dict[str, Any]:
    """Analyze repository security aspects."""
    security_issues = []
    
    try:
        # Check for sensitive files
        sensitive_patterns = [
            r"\.env$",
            r"\.key$",
            r"\.pem$",
            r"password",
            r"secret",
            r"token"
        ]
        
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            for file in files:
                for pattern in sensitive_patterns:
                    if re.search(pattern, file, re.IGNORECASE):
                        security_issues.append({
                            "type": "sensitive_file",
                            "file": file,
                            "pattern": pattern
                        })
        
        # Check for large binary files that might contain secrets
        large_files = find_large_files(repo_path, size_threshold=1024*1024)  # 1MB
        
        return {
            "security_issues": security_issues,
            "large_binary_files": large_files,
            "security_score": calculate_security_score(security_issues, large_files)
        }
        
    except Exception as e:
        return {"error": str(e)}


def check_git_best_practices(repo_path: str) -> Dict[str, Any]:
    """Check adherence to Git best practices."""
    practices = {}
    
    # Check for .gitignore
    practices["has_gitignore"] = os.path.exists(os.path.join(repo_path, ".gitignore"))
    
    # Check for README
    readme_files = ["README.md", "README.rst", "README.txt", "README"]
    practices["has_readme"] = any(os.path.exists(os.path.join(repo_path, f)) for f in readme_files)
    
    # Check for hooks directory
    hooks_dir = os.path.join(repo_path, ".git", "hooks")
    if os.path.exists(hooks_dir):
        hook_files = [f for f in os.listdir(hooks_dir) if not f.endswith('.sample')]
        practices["has_custom_hooks"] = len(hook_files) > 0
    else:
        practices["has_custom_hooks"] = False
    
    # Check commit message format
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            conventional_commits = sum(1 for commit in commits if is_conventional_commit(commit))
            practices["conventional_commits_ratio"] = conventional_commits / len(commits) if commits else 0
    except:
        practices["conventional_commits_ratio"] = 0
    
    return practices


# Additional helper functions
def find_large_files(repo_path: str, size_threshold: int = 10*1024*1024) -> List[Dict[str, Any]]:
    """Find large files in repository."""
    large_files = []
    
    try:
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > size_threshold:
                        rel_path = os.path.relpath(file_path, repo_path)
                        large_files.append({
                            "file": rel_path,
                            "size": size,
                            "size_mb": size / (1024 * 1024)
                        })
                except:
                    continue
    except:
        pass
    
    return sorted(large_files, key=lambda x: x["size"], reverse=True)


def analyze_branch_patterns(branches: List[str]) -> Dict[str, Any]:
    """Analyze branch naming patterns."""
    patterns = {
        "feature_branches": 0,
        "bugfix_branches": 0,
        "release_branches": 0,
        "hotfix_branches": 0,
        "development_branches": 0,
        "other_branches": 0
    }
    
    for branch in branches:
        branch = branch.strip()
        if branch.startswith('feature/') or 'feature' in branch:
            patterns["feature_branches"] += 1
        elif branch.startswith('bugfix/') or branch.startswith('fix/') or 'bugfix' in branch:
            patterns["bugfix_branches"] += 1
        elif branch.startswith('release/') or 'release' in branch:
            patterns["release_branches"] += 1
        elif branch.startswith('hotfix/') or 'hotfix' in branch:
            patterns["hotfix_branches"] += 1
        elif branch in ['develop', 'development', 'dev']:
            patterns["development_branches"] += 1
        else:
            patterns["other_branches"] += 1
    
    return patterns


def find_stale_branches(repo_path: str, days_threshold: int = 90) -> List[str]:
    """Find stale branches."""
    stale_branches = []
    
    try:
        result = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short) %(committerdate)", "refs/heads"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            import datetime
            threshold_date = datetime.datetime.now() - datetime.timedelta(days=days_threshold)
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        branch, date_str = parts
                        try:
                            # Parse git date format
                            commit_date = datetime.datetime.strptime(date_str.split(' +')[0], '%a %b %d %H:%M:%S %Y')
                            if commit_date < threshold_date:
                                stale_branches.append(branch)
                        except:
                            continue
    except:
        pass
    
    return stale_branches


def infer_branch_strategy(branches: List[str]) -> str:
    """Infer the branching strategy used."""
    branch_names = [b.strip() for b in branches]
    
    if 'develop' in branch_names and any('release/' in b for b in branch_names):
        return "git-flow"
    elif any('feature/' in b for b in branch_names):
        return "feature-branch"
    elif len(branch_names) <= 2:
        return "simple"
    else:
        return "custom"


def analyze_commit_messages(commits: List[str]) -> Dict[str, Any]:
    """Analyze commit message quality."""
    if not commits or commits == ['']:
        return {"error": "No commits to analyze"}
    
    conventional_count = sum(1 for commit in commits if is_conventional_commit(commit))
    
    # Analyze message length
    message_lengths = []
    for commit in commits:
        if commit.strip():
            # Remove hash and extract message
            message = ' '.join(commit.split()[1:])
            message_lengths.append(len(message))
    
    avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    
    return {
        "total_commits": len(commits),
        "conventional_commits": conventional_count,
        "conventional_ratio": conventional_count / len(commits),
        "average_message_length": avg_length,
        "quality_score": calculate_commit_message_quality(conventional_count, len(commits), avg_length)
    }


def is_conventional_commit(commit: str) -> bool:
    """Check if commit follows conventional commit format."""
    if not commit.strip():
        return False
    
    # Remove hash and extract message
    message = ' '.join(commit.split()[1:])
    
    # Check for conventional commit pattern
    pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
    return bool(re.match(pattern, message))


def analyze_commit_frequency(repo_path: str) -> Dict[str, Any]:
    """Analyze commit frequency patterns."""
    try:
        # Get commits by week for the last 3 months
        result = subprocess.run(
            ["git", "log", "--since='12 weeks ago'", "--pretty=format:%cd", "--date=format:%Y-%U"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            weeks = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Count commits per week
            week_counts = {}
            for week in weeks:
                week_counts[week] = week_counts.get(week, 0) + 1
            
            # Calculate statistics
            if week_counts:
                values = list(week_counts.values())
                avg_per_week = sum(values) / len(values)
                max_per_week = max(values)
                min_per_week = min(values)
            else:
                avg_per_week = max_per_week = min_per_week = 0
            
            return {
                "commits_per_week": week_counts,
                "average_per_week": avg_per_week,
                "max_per_week": max_per_week,
                "min_per_week": min_per_week,
                "activity_pattern": classify_activity_pattern(avg_per_week)
            }
    except:
        pass
    
    return {"error": "Could not analyze commit frequency"}


def classify_activity_pattern(avg_per_week: float) -> str:
    """Classify development activity pattern."""
    if avg_per_week > 20:
        return "very_active"
    elif avg_per_week > 10:
        return "active"
    elif avg_per_week > 5:
        return "moderate"
    elif avg_per_week > 1:
        return "low"
    else:
        return "inactive"


def calculate_commit_quality_score(conventional_count: int, total_commits: int, avg_length: float) -> int:
    """Calculate commit message quality score."""
    score = 0
    
    # Conventional commits (max 40 points)
    if total_commits > 0:
        conventional_ratio = conventional_count / total_commits
        score += conventional_ratio * 40
    
    # Message length (max 30 points)
    if 20 <= avg_length <= 72:  # Ideal length
        score += 30
    elif 10 <= avg_length <= 100:  # Acceptable
        score += 20
    else:
        score += 10
    
    # Consistency bonus (max 30 points)
    if conventional_count / total_commits > 0.8:
        score += 30
    elif conventional_count / total_commits > 0.5:
        score += 20
    else:
        score += 10
    
    return min(100, int(score))


def analyze_contribution_distribution(contributors: List[Dict]) -> Dict[str, Any]:
    """Analyze contribution distribution among contributors."""
    if not contributors:
        return {"pattern": "no_data"}
    
    total_commits = sum(c["commits"] for c in contributors)
    
    # Calculate concentration
    if len(contributors) == 1:
        pattern = "single_contributor"
    elif contributors[0]["commits"] / total_commits > 0.8:
        pattern = "dominated_by_one"
    elif len(contributors) > 5 and contributors[0]["commits"] / total_commits < 0.5:
        pattern = "well_distributed"
    else:
        pattern = "balanced"
    
    return {
        "pattern": pattern,
        "gini_coefficient": calculate_gini_coefficient([c["commits"] for c in contributors]),
        "top_contributor_percentage": contributors[0]["commits"] / total_commits if contributors else 0
    }


def calculate_gini_coefficient(values: List[int]) -> float:
    """Calculate Gini coefficient for contribution inequality."""
    if not values:
        return 0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumsum = sum((i + 1) * v for i, v in enumerate(sorted_values))
    return (2 * cumsum) / (n * sum(sorted_values)) - (n + 1) / n


def analyze_python_structure(files: List[str]) -> Dict[str, Any]:
    """Analyze Python project structure."""
    structure = {
        "has_setup_py": "setup.py" in files,
        "has_pyproject_toml": "pyproject.toml" in files,
        "has_requirements_txt": "requirements.txt" in files,
        "has_src_layout": any(f.startswith("src/") for f in files),
        "has_tests_dir": any(f.startswith("tests/") or f.startswith("test/") for f in files),
        "has_docs_dir": any(f.startswith("docs/") for f in files),
        "python_files": len([f for f in files if f.endswith(".py")]),
        "package_structure": infer_package_structure(files)
    }
    
    return structure


def infer_package_structure(files: List[str]) -> str:
    """Infer Python package structure type."""
    has_src = any(f.startswith("src/") for f in files)
    has_package_init = any("__init__.py" in f for f in files)
    
    if has_src and has_package_init:
        return "src_layout"
    elif has_package_init:
        return "flat_layout"
    elif any(f.endswith(".py") for f in files):
        return "script_collection"
    else:
        return "unknown"


def calculate_organization_score(files: List[str]) -> int:
    """Calculate project organization score."""
    score = 0
    
    # Basic structure (max 40 points)
    if "README.md" in files or "README.rst" in files:
        score += 10
    if ".gitignore" in files:
        score += 10
    if "requirements.txt" in files or "pyproject.toml" in files:
        score += 10
    if any(f.startswith("tests/") for f in files):
        score += 10
    
    # Python-specific structure (max 30 points)
    python_files = [f for f in files if f.endswith(".py")]
    if python_files:
        if any("__init__.py" in f for f in files):
            score += 15
        if "setup.py" in files or "pyproject.toml" in files:
            score += 15
    
    # Documentation (max 20 points)
    if any(f.startswith("docs/") for f in files):
        score += 20
    
    # CI/CD (max 10 points)
    if any(f.startswith(".github/") or f.startswith(".gitlab/") for f in files):
        score += 10
    
    return min(100, score)


def infer_workflow_type(merge_commits: int, total_commits: int) -> str:
    """Infer Git workflow type from commit patterns."""
    if total_commits == 0:
        return "unknown"
    
    merge_ratio = merge_commits / total_commits
    
    if merge_ratio > 0.3:
        return "merge_heavy"
    elif merge_ratio > 0.1:
        return "feature_branch"
    else:
        return "linear"


def assess_workflow_health(merge_commits: int, total_commits: int) -> Dict[str, Any]:
    """Assess Git workflow health."""
    if total_commits == 0:
        return {"status": "no_data"}
    
    merge_ratio = merge_commits / total_commits
    
    if merge_ratio > 0.5:
        status = "concerning"
        issues = ["Too many merge commits", "Consider rebasing or squashing"]
    elif merge_ratio > 0.3:
        status = "needs_attention"
        issues = ["High merge commit ratio", "Review branching strategy"]
    else:
        status = "healthy"
        issues = []
    
    return {
        "status": status,
        "merge_ratio": merge_ratio,
        "issues": issues
    }


def calculate_security_score(security_issues: List[Dict], large_files: List[Dict]) -> int:
    """Calculate repository security score."""
    score = 100
    
    # Deduct for security issues
    for issue in security_issues:
        if issue["type"] == "sensitive_file":
            score -= 20
    
    # Deduct for large files (potential binary/secret files)
    for file in large_files:
        if file["size_mb"] > 10:  # Very large files
            score -= 10
        elif file["size_mb"] > 5:
            score -= 5
    
    return max(0, score)


def calculate_commit_message_quality(conventional_count: int, total_commits: int, avg_length: float) -> int:
    """Calculate commit message quality score."""
    if total_commits == 0:
        return 0
    
    score = 0
    
    # Conventional commits
    conventional_ratio = conventional_count / total_commits
    score += conventional_ratio * 50
    
    # Message length
    if 30 <= avg_length <= 72:
        score += 30
    elif 20 <= avg_length <= 100:
        score += 20
    else:
        score += 10
    
    # Consistency
    if conventional_ratio > 0.8:
        score += 20
    elif conventional_ratio > 0.5:
        score += 10
    
    return min(100, int(score))


def generate_git_recommendations(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate expert Git recommendations."""
    recommendations = []
    
    # Repository health recommendations
    repo_health = analysis.get("repository_health", {})
    missing_files = repo_health.get("important_files", {}).get("missing", [])
    
    if ".gitignore" in missing_files:
        recommendations.append({
            "category": "repository_setup",
            "priority": "high",
            "title": "Add .gitignore file",
            "description": "Create a comprehensive .gitignore to exclude unwanted files",
            "action": "Create .gitignore with Python, IDE, and OS-specific patterns"
        })
    
    if "README.md" in missing_files:
        recommendations.append({
            "category": "documentation",
            "priority": "high",
            "title": "Add README.md",
            "description": "Create project documentation with setup and usage instructions",
            "action": "Write clear README with project description, installation, and examples"
        })
    
    # Commit quality recommendations
    commit_analysis = analysis.get("commit_analysis", {}).get("commit_message_analysis", {})
    if commit_analysis.get("conventional_ratio", 0) < 0.5:
        recommendations.append({
            "category": "commit_quality",
            "priority": "medium",
            "title": "Improve commit message format",
            "description": "Use conventional commit format for better change tracking",
            "action": "Use format: type(scope): description (e.g., feat(auth): add user login)"
        })
    
    # Branch recommendations
    branch_analysis = analysis.get("branch_analysis", {})
    if branch_analysis.get("stale_branches"):
        recommendations.append({
            "category": "branch_management",
            "priority": "medium",
            "title": "Clean up stale branches",
            "description": "Remove old branches that are no longer needed",
            "action": f"Delete {len(branch_analysis['stale_branches'])} stale branches"
        })
    
    # Security recommendations
    security_analysis = analysis.get("security_analysis", {})
    if security_analysis.get("security_issues"):
        recommendations.append({
            "category": "security",
            "priority": "critical",
            "title": "Address security issues",
            "description": "Remove sensitive files and potential secrets from repository",
            "action": "Review and remove sensitive files, use .gitignore to prevent future issues"
        })
    
    return recommendations


def calculate_repository_score(analysis: Dict[str, Any]) -> int:
    """Calculate overall repository score."""
    scores = []
    
    # Repository health score
    repo_health = analysis.get("repository_health", {})
    if "important_files" in repo_health:
        scores.append(repo_health["important_files"]["score"])
    
    # Commit quality score
    commit_analysis = analysis.get("commit_analysis", {}).get("commit_message_analysis", {})
    if "quality_score" in commit_analysis:
        scores.append(commit_analysis["quality_score"])
    
    # File organization score
    file_analysis = analysis.get("file_analysis", {})
    if "organization_score" in file_analysis:
        scores.append(file_analysis["organization_score"])
    
    # Security score
    security_analysis = analysis.get("security_analysis", {})
    if "security_score" in security_analysis:
        scores.append(security_analysis["security_score"])
    
    # Best practices score
    best_practices = analysis.get("best_practices", {})
    practices_score = 0
    if best_practices.get("has_gitignore"):
        practices_score += 25
    if best_practices.get("has_readme"):
        practices_score += 25
    if best_practices.get("has_custom_hooks"):
        practices_score += 25
    if best_practices.get("conventional_commits_ratio", 0) > 0.5:
        practices_score += 25
    scores.append(practices_score)
    
    return int(sum(scores) / len(scores)) if scores else 0


def identify_quick_wins(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify quick wins for repository improvement."""
    quick_wins = []
    
    repo_health = analysis.get("repository_health", {})
    missing_files = repo_health.get("important_files", {}).get("missing", [])
    
    if ".gitignore" in missing_files:
        quick_wins.append({
            "action": "Add .gitignore file",
            "effort": "5 minutes",
            "impact": "high"
        })
    
    if "README.md" in missing_files:
        quick_wins.append({
            "action": "Create basic README.md",
            "effort": "15 minutes",
            "impact": "high"
        })
    
    branch_analysis = analysis.get("branch_analysis", {})
    if branch_analysis.get("stale_branches"):
        quick_wins.append({
            "action": f"Delete {len(branch_analysis['stale_branches'])} stale branches",
            "effort": "10 minutes",
            "impact": "medium"
        })
    
    best_practices = analysis.get("best_practices", {})
    if not best_practices.get("has_custom_hooks"):
        quick_wins.append({
            "action": "Add pre-commit hook for code quality",
            "effort": "20 minutes",
            "impact": "high"
        })
    
    return quick_wins


# Workflow suggestion functions
def determine_optimal_workflow(project_type: str, team_size: int) -> str:
    """Determine optimal Git workflow."""
    if team_size == 1:
        return "simple"
    elif team_size <= 3 and project_type != "enterprise":
        return "github-flow"
    elif project_type == "enterprise" or team_size > 10:
        return "git-flow"
    else:
        return "feature-branch"


def generate_workflow_implementation(workflow: str, project_type: str, team_size: int) -> Dict[str, Any]:
    """Generate workflow implementation guide."""
    implementations = {
        "simple": {
            "description": "Simple linear workflow for solo development",
            "steps": [
                "Work directly on main branch",
                "Make frequent, small commits",
                "Use conventional commit messages",
                "Tag releases when needed"
            ],
            "commands": [
                "git add .",
                "git commit -m 'feat: add new feature'",
                "git push origin main",
                "git tag v1.0.0"
            ]
        },
        "github-flow": {
            "description": "Lightweight branching model for continuous deployment",
            "steps": [
                "Create feature branch from main",
                "Make changes and commit",
                "Open pull request",
                "Review and merge to main",
                "Deploy from main"
            ],
            "commands": [
                "git checkout -b feature/new-feature",
                "git commit -m 'feat: add new feature'",
                "git push origin feature/new-feature",
                "# Create PR via GitHub",
                "git checkout main && git pull"
            ]
        },
        "git-flow": {
            "description": "Robust branching model for release-based projects",
            "steps": [
                "Maintain main and develop branches",
                "Create feature branches from develop",
                "Create release branches for testing",
                "Merge releases to main and develop",
                "Use hotfix branches for urgent fixes"
            ],
            "commands": [
                "git flow init",
                "git flow feature start new-feature",
                "git flow feature finish new-feature",
                "git flow release start 1.0.0",
                "git flow release finish 1.0.0"
            ]
        },
        "feature-branch": {
            "description": "Feature-based branching with code review",
            "steps": [
                "Create feature branch for each feature",
                "Develop and test in feature branch",
                "Create pull request for review",
                "Merge after approval",
                "Delete feature branch"
            ],
            "commands": [
                "git checkout -b feature/PROJ-123-new-feature",
                "git commit -m 'feat(feature): implement new functionality'",
                "git push origin feature/PROJ-123-new-feature",
                "# Create PR and review",
                "git branch -d feature/PROJ-123-new-feature"
            ]
        }
    }
    
    return implementations.get(workflow, implementations["github-flow"])


def create_branch_strategy(workflow: str, project_type: str) -> Dict[str, Any]:
    """Create branch strategy based on workflow."""
    strategies = {
        "simple": {
            "main_branches": ["main"],
            "supporting_branches": [],
            "naming_convention": "No specific convention needed",
            "protection_rules": ["Protect main branch", "Require PR reviews"]
        },
        "github-flow": {
            "main_branches": ["main"],
            "supporting_branches": ["feature/*"],
            "naming_convention": "feature/description or feature/issue-number",
            "protection_rules": ["Protect main", "Require PR reviews", "Require status checks"]
        },
        "git-flow": {
            "main_branches": ["main", "develop"],
            "supporting_branches": ["feature/*", "release/*", "hotfix/*"],
            "naming_convention": "feature/name, release/version, hotfix/name",
            "protection_rules": ["Protect main and develop", "Require PR reviews", "No direct commits"]
        },
        "feature-branch": {
            "main_branches": ["main"],
            "supporting_branches": ["feature/*", "bugfix/*", "hotfix/*"],
            "naming_convention": "type/issue-description or type/PROJ-123",
            "protection_rules": ["Protect main", "Require PR reviews", "Require CI checks"]
        }
    }
    
    return strategies.get(workflow, strategies["github-flow"])


def suggest_workflow_automation(workflow: str, project_type: str) -> List[Dict[str, Any]]:
    """Suggest workflow automation tools and practices."""
    automations = []
    
    # CI/CD suggestions
    if project_type == "web":
        automations.append({
            "type": "ci_cd",
            "tool": "GitHub Actions",
            "purpose": "Automated testing and deployment",
            "config": "Trigger on PR and main branch pushes"
        })
    
    # Code quality automation
    automations.append({
        "type": "code_quality",
        "tool": "pre-commit",
        "purpose": "Automated code formatting and linting",
        "config": "Install pre-commit hooks for consistent code quality"
    })
    
    # Dependency management
    if project_type in ["web", "library"]:
        automations.append({
            "type": "dependency_management",
            "tool": "Dependabot",
            "purpose": "Automated dependency updates",
            "config": "Configure dependabot.yml for security updates"
        })
    
    # Release automation
    if workflow in ["git-flow", "github-flow"]:
        automations.append({
            "type": "release_automation",
            "tool": "semantic-release",
            "purpose": "Automated versioning and releases",
            "config": "Use conventional commits for automatic version bumping"
        })
    
    return automations


def get_workflow_expert_tips(workflow: str, team_size: int) -> List[str]:
    """Get expert tips for specific workflow."""
    base_tips = [
        "Keep commits small and focused on one change",
        "Write clear, descriptive commit messages",
        "Use conventional commit format for automation",
        "Review code before merging to main branches",
        "Set up branch protection rules",
        "Use tags for releases",
        "Clean up merged branches regularly"
    ]
    
    workflow_specific = {
        "git-flow": [
            "Never commit directly to main or develop",
            "Use git-flow CLI tools for consistency",
            "Merge release branches to both main and develop",
            "Always start hotfixes from main branch"
        ],
        "github-flow": [
            "Keep feature branches short-lived",
            "Deploy main branch frequently",
            "Use feature flags for incomplete features",
            "Automate deployment from main branch"
        ],
        "feature-branch": [
            "Link branches to issue tracking system",
            "Use meaningful branch names with issue numbers",
            "Rebase feature branches before merging",
            "Squash commits when merging if needed"
        ]
    }
    
    tips = base_tips + workflow_specific.get(workflow, [])
    
    if team_size > 5:
        tips.extend([
            "Establish clear code review guidelines",
            "Use CODEOWNERS file for automatic reviewers",
            "Implement required status checks",
            "Consider using draft PRs for work in progress"
        ])
    
    return tips


# Hook generation functions
def generate_hook_installation_script(hooks: Dict[str, Any]) -> str:
    """Generate script to install Git hooks."""
    script = """#!/bin/bash
# Git hooks installation script

set -e

echo "Installing Git hooks..."

# Check if we're in a Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a Git repository"
    exit 1
fi

HOOKS_DIR=".git/hooks"

"""
    
    for hook_name, hook_data in hooks.items():
        script += f"""
# Install {hook_name} hook
echo "Installing {hook_name} hook..."
cat > "$HOOKS_DIR/{hook_name}" << 'EOF'
{hook_data['script']}
EOF

chmod +x "$HOOKS_DIR/{hook_name}"
echo "{hook_name} hook installed successfully"
"""
    
    script += """
echo "All hooks installed successfully!"
echo "Note: Install required dependencies if needed"
"""
    
    return script


def suggest_hook_tooling() -> List[Dict[str, Any]]:
    """Suggest additional hook tooling."""
    return [
        {
            "tool": "pre-commit",
            "purpose": "Hook management framework",
            "installation": "pip install pre-commit",
            "benefits": ["Easy hook configuration", "Multi-language support", "Hook sharing"]
        },
        {
            "tool": "husky",
            "purpose": "Git hooks for Node.js projects",
            "installation": "npm install --save-dev husky",
            "benefits": ["Simple setup", "JSON configuration", "Popular in JS ecosystem"]
        },
        {
            "tool": "lefthook",
            "purpose": "Fast Git hooks manager",
            "installation": "brew install lefthook",
            "benefits": ["Fast execution", "Parallel processing", "YAML configuration"]
        }
    ]


def get_git_hooks_guidance() -> List[str]:
    """Get expert guidance for Git hooks."""
    return [
        "Keep hooks fast - developers will disable slow hooks",
        "Make hooks idempotent - safe to run multiple times",
        "Provide clear error messages with fix suggestions",
        "Allow bypassing hooks with --no-verify when necessary",
        "Test hooks thoroughly before deploying to team",
        "Document what each hook does and why",
        "Consider using hook management tools for complex setups",
        "Share hooks with team through repository or package manager"
    ]


# Code change analysis functions
def get_changed_files(since_ref: str) -> List[Dict[str, Any]]:
    """Get files changed since reference."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", since_ref],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        changed_files = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    filename = parts[1]
                    changed_files.append({
                        "file": filename,
                        "status": status,
                        "change_type": get_change_type(status)
                    })
        
        return changed_files
        
    except Exception:
        return []


def get_change_type(status: str) -> str:
    """Get human-readable change type."""
    type_map = {
        'A': 'added',
        'M': 'modified', 
        'D': 'deleted',
        'R': 'renamed',
        'C': 'copied',
        'T': 'type_changed'
    }
    return type_map.get(status[0], 'unknown')


def analyze_change_patterns(changed_files: List[Dict], since_ref: str) -> Dict[str, Any]:
    """Analyze patterns in changed files."""
    if not changed_files:
        return {"total_files": 0}
    
    # File type analysis
    file_types = {}
    for file_info in changed_files:
        ext = os.path.splitext(file_info["file"])[1]
        file_types[ext] = file_types.get(ext, 0) + 1
    
    # Change type analysis
    change_types = {}
    for file_info in changed_files:
        change_type = file_info["change_type"]
        change_types[change_type] = change_types.get(change_type, 0) + 1
    
    # Risk assessment
    high_risk_files = [f for f in changed_files if is_high_risk_file(f["file"])]
    
    return {
        "total_files": len(changed_files),
        "file_types": file_types,
        "change_types": change_types,
        "high_risk_files": high_risk_files,
        "complexity_score": calculate_change_complexity(changed_files)
    }


def is_high_risk_file(filename: str) -> bool:
    """Check if file is high risk for changes."""
    high_risk_patterns = [
        r"migrations?/",
        r"settings?\.py",
        r"config",
        r"requirements",
        r"setup\.py",
        r"pyproject\.toml",
        r"Dockerfile",
        r"\.github/workflows/",
        r"auth",
        r"security"
    ]
    
    return any(re.search(pattern, filename, re.IGNORECASE) for pattern in high_risk_patterns)


def calculate_change_complexity(changed_files: List[Dict]) -> int:
    """Calculate complexity score for changes."""
    score = len(changed_files)  # Base score
    
    # Add complexity for different file types
    for file_info in changed_files:
        filename = file_info["file"]
        
        if filename.endswith(('.py', '.js', '.ts')):
            score += 2  # Code files
        elif filename.endswith(('.yaml', '.yml', '.json')):
            score += 1  # Config files
        elif is_high_risk_file(filename):
            score += 5  # High-risk files
    
    return score


def identify_review_focus_areas(change_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify areas that need focused review."""
    focus_areas = []
    
    # High-risk files
    high_risk_files = change_analysis.get("high_risk_files", [])
    if high_risk_files:
        focus_areas.append({
            "area": "High-Risk Files",
            "priority": "critical",
            "files": [f["file"] for f in high_risk_files],
            "reason": "These files can significantly impact system behavior"
        })
    
    # Large number of changes
    if change_analysis.get("total_files", 0) > 20:
        focus_areas.append({
            "area": "Large Changeset",
            "priority": "high",
            "reason": "Large changesets are harder to review thoroughly",
            "suggestion": "Consider breaking into smaller PRs"
        })
    
    # Database migrations
    file_types = change_analysis.get("file_types", {})
    if any("migration" in f for f in change_analysis.get("high_risk_files", [])):
        focus_areas.append({
            "area": "Database Changes",
            "priority": "high",
            "reason": "Database migrations can affect data integrity",
            "suggestion": "Review migration scripts carefully and test on staging"
        })
    
    # Security-related changes
    if any("auth" in f["file"] or "security" in f["file"] for f in change_analysis.get("high_risk_files", [])):
        focus_areas.append({
            "area": "Security Changes",
            "priority": "critical",
            "reason": "Security changes require careful review",
            "suggestion": "Involve security expert in review"
        })
    
    return focus_areas


def generate_code_review_checklist(change_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate context-specific code review checklist."""
    checklist = []
    
    # General checklist items
    checklist.extend([
        {"category": "Code Quality", "item": "Code follows project style guidelines"},
        {"category": "Code Quality", "item": "Functions and classes have clear, descriptive names"},
        {"category": "Code Quality", "item": "Code is properly commented and documented"},
        {"category": "Testing", "item": "New functionality has appropriate tests"},
        {"category": "Testing", "item": "Tests are clear and test the right behavior"},
        {"category": "Security", "item": "No sensitive information is exposed"},
        {"category": "Performance", "item": "No obvious performance issues"}
    ])
    
    # Context-specific items
    file_types = change_analysis.get("file_types", {})
    
    if ".py" in file_types:
        checklist.extend([
            {"category": "Python", "item": "Imports are organized and necessary"},
            {"category": "Python", "item": "Type hints are used where appropriate"},
            {"category": "Python", "item": "Error handling is appropriate"},
            {"category": "Python", "item": "No obvious code smells (long functions, god classes, etc.)"}
        ])
    
    if any(f["file"].endswith(('.yaml', '.yml', '.json')) for f in change_analysis.get("high_risk_files", [])):
        checklist.extend([
            {"category": "Configuration", "item": "Configuration changes are documented"},
            {"category": "Configuration", "item": "No hardcoded secrets in config files"},
            {"category": "Configuration", "item": "Configuration is validated"}
        ])
    
    return checklist


def assess_change_risk(change_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess risk level of changes."""
    risk_factors = []
    risk_score = 0
    
    # Number of files
    total_files = change_analysis.get("total_files", 0)
    if total_files > 50:
        risk_factors.append("Very large changeset")
        risk_score += 30
    elif total_files > 20:
        risk_factors.append("Large changeset")
        risk_score += 15
    
    # High-risk files
    high_risk_count = len(change_analysis.get("high_risk_files", []))
    if high_risk_count > 0:
        risk_factors.append(f"{high_risk_count} high-risk files changed")
        risk_score += high_risk_count * 10
    
    # Complexity
    complexity = change_analysis.get("complexity_score", 0)
    if complexity > 100:
        risk_factors.append("High complexity changes")
        risk_score += 20
    
    # Determine risk level
    if risk_score > 60:
        risk_level = "high"
    elif risk_score > 30:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_score": min(100, risk_score),
        "risk_factors": risk_factors,
        "recommendations": generate_risk_recommendations(risk_level, risk_factors)
    }


def generate_risk_recommendations(risk_level: str, risk_factors: List[str]) -> List[str]:
    """Generate recommendations based on risk assessment."""
    recommendations = []
    
    if risk_level == "high":
        recommendations.extend([
            "Consider breaking this into smaller, focused PRs",
            "Require multiple reviewers",
            "Deploy to staging environment first",
            "Plan rollback strategy before deployment"
        ])
    elif risk_level == "medium":
        recommendations.extend([
            "Ensure thorough testing before merge",
            "Consider requiring additional reviewer",
            "Test in staging environment"
        ])
    
    # Specific recommendations based on risk factors
    for factor in risk_factors:
        if "high-risk files" in factor:
            recommendations.append("Have domain expert review high-risk file changes")
        elif "large changeset" in factor:
            recommendations.append("Consider breaking into multiple smaller PRs")
        elif "complexity" in factor:
            recommendations.append("Focus review on complex logic and edge cases")
    
    return recommendations


def get_code_review_expert_tips() -> List[str]:
    """Get expert tips for code review."""
    return [
        "Review code, not the person - focus on the changes",
        "Look for the 'why' behind changes, not just the 'what'",
        "Check for edge cases and error handling",
        "Verify that tests actually test the intended behavior",
        "Consider maintainability and future development",
        "Look for security implications of changes",
        "Check that documentation is updated if needed",
        "Suggest improvements, don't just point out problems",
        "Use automated tools to catch style and basic issues",
        "Take time for thorough review - rushing leads to bugs in production"
    ]


# Git bisect helper functions
def analyze_bisect_strategy(error_description: str) -> Dict[str, Any]:
    """Analyze error description to suggest bisect strategy."""
    strategy = {
        "approach": "automatic",
        "focus_areas": [],
        "test_strategy": "script"
    }
    
    # Analyze error type
    if any(word in error_description.lower() for word in ["test", "unit", "fail"]):
        strategy["focus_areas"].append("test failures")
        strategy["test_strategy"] = "run specific test"
    
    if any(word in error_description.lower() for word in ["performance", "slow", "timeout"]):
        strategy["focus_areas"].append("performance regression")
        strategy["test_strategy"] = "performance benchmark"
    
    if any(word in error_description.lower() for word in ["crash", "segfault", "exception"]):
        strategy["focus_areas"].append("runtime errors")
        strategy["test_strategy"] = "reproduction script"
    
    if any(word in error_description.lower() for word in ["ui", "interface", "display"]):
        strategy["focus_areas"].append("user interface")
        strategy["approach"] = "manual"
        strategy["test_strategy"] = "manual verification"
    
    return strategy


def generate_bisect_commands(last_known_good: str, strategy: Dict[str, Any]) -> List[str]:
    """Generate Git bisect commands."""
    commands = []
    
    # Start bisect
    commands.append("git bisect start")
    
    # Mark current commit as bad
    commands.append("git bisect bad")
    
    # Mark last known good commit
    if last_known_good:
        commands.append(f"git bisect good {last_known_good}")
    else:
        commands.append("# git bisect good <last-known-good-commit>")
        commands.append("# Find a good commit with: git log --oneline")
    
    # Add test script if automated
    if strategy.get("approach") == "automatic":
        commands.extend([
            "# Create test script (bisect_test.sh):",
            "# #!/bin/bash",
            "# your_test_command_here",
            "# exit 0 if good, 1 if bad",
            "",
            "chmod +x bisect_test.sh",
            "git bisect run ./bisect_test.sh"
        ])
    else:
        commands.extend([
            "# Manual bisect process:",
            "# 1. Test current commit",
            "# 2. git bisect good (if working) or git bisect bad (if broken)",
            "# 3. Repeat until bisect finds the problematic commit",
            "",
            "# When done:",
            "git bisect reset"
        ])
    
    return commands


def suggest_bisect_test_script(error_description: str) -> str:
    """Suggest test script for Git bisect."""
    script = """#!/bin/bash
# Git bisect test script
# Exit 0 if commit is good, 1 if bad

set -e

"""
    
    # Add specific test based on error description
    if "test" in error_description.lower():
        script += """# Run specific test
python -m pytest tests/test_specific.py
exit $?
"""
    elif "build" in error_description.lower():
        script += """# Test build
python setup.py build
exit $?
"""
    elif "import" in error_description.lower():
        script += """# Test import
python -c "import your_module"
exit $?
"""
    else:
        script += """# Generic test - replace with your specific test
python -c "
# Add your test logic here
# Raise exception or exit with non-zero code if bad
print('Testing...')
"
exit $?
"""
    
    return script


def get_bisect_expert_guidance(error_description: str) -> List[str]:
    """Get expert guidance for Git bisect."""
    guidance = [
        "Start with a wide range - find a commit you know was working",
        "Write a reliable test script that consistently reproduces the issue",
        "Use 'git bisect skip' if a commit can't be tested (build fails, etc.)",
        "Keep the test script simple and fast",
        "Make sure your test is deterministic",
        "Test the script on known good and bad commits first",
        "Use 'git bisect log' to see the current bisect state",
        "Use 'git bisect visualize' to see remaining commits graphically"
    ]
    
    # Add specific guidance based on error type
    if "performance" in error_description.lower():
        guidance.extend([
            "For performance issues, use consistent test conditions",
            "Run multiple iterations and average the results",
            "Consider system load when testing performance"
        ])
    elif "intermittent" in error_description.lower():
        guidance.extend([
            "For intermittent issues, run tests multiple times",
            "Consider using 'git bisect skip' for unclear results",
            "May need to test each commit several times"
        ])
    
    return guidance


def estimate_bisect_commits() -> Dict[str, Any]:
    """Estimate number of commits to test in bisect."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            total_commits = int(result.stdout.strip())
            
            # Estimate bisect steps (log2 of range)
            import math
            estimated_steps = math.ceil(math.log2(total_commits))
            
            return {
                "total_commits": total_commits,
                "estimated_steps": estimated_steps,
                "time_estimate": f"{estimated_steps * 5} minutes (assuming 5 min per test)"
            }
    except:
        pass
    
    return {
        "estimated_steps": "unknown",
        "time_estimate": "depends on commit range and test complexity"
    }
