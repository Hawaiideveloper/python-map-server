

def safe_read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

def safe_write_file(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)
