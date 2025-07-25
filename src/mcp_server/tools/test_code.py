
import os
import subprocess
import tempfile


def test_python(code: str):
    """
    Write code to temp file, run pytest on it, and return results.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test_code.py")
        with open(file_path, "w") as f:
            f.write(code)
        result = subprocess.run(
            ["pytest", file_path, "--maxfail=1", "--disable-warnings", "-q"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"pytest_stdout": result.stdout, "pytest_stderr": result.stderr, "returncode": result.returncode}
