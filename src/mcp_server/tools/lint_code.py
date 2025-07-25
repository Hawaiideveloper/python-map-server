
import subprocess
import tempfile


def lint_python(code: str):
    """
    Lint Python code using ruff and return the lint messages.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as tmp:
        tmp.write(code)
        tmp.flush()
        result = subprocess.run(
            ["ruff", tmp.name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {"lint_output": result.stdout, "returncode": result.returncode}
