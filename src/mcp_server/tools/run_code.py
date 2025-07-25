
import subprocess
import tempfile
import traceback
import sys

def run_python(code: str):
    """
    Execute Python code safely using a subprocess and return output.
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as tmp:
            tmp.write(code)
            tmp.flush()
            result = subprocess.run(
                [sys.executable, tmp.name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
