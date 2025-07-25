
import subprocess
import tempfile

def format_python(code: str):
    """
    Format Python code using black and return formatted code.
    """
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=True) as tmp:
        tmp.write(code)
        tmp.flush()
        subprocess.run(["black", tmp.name], check=True)
        tmp.seek(0)
        formatted = tmp.read()
        return {"formatted_code": formatted}
