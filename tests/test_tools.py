
from mcp_server.tools import format_code, lint_code, run_code


def test_run_code():
    code = "print('Hello World')"
    result = run_code.run_python(code)
    assert "Hello World" in result["stdout"]

def test_lint_code():
    bad_code = "import os\n\n\n"
    result = lint_code.lint_python(bad_code)
    assert isinstance(result["lint_output"], str)

def test_format_code():
    ugly_code = "x=1+1"
    result = format_code.format_python(ugly_code)
    assert "x = 1 + 1" in result["formatted_code"]
