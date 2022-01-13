from pathlib import Path


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

 
