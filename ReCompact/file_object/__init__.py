def create_empty_file(filename):
    import os.path
    from pathlib import Path
    file = Path(filename)
    if not os.path.isdir(file.parent.absolute()):
        os.mkdir(file.parent.absolute())
    file.touch(exist_ok=True)


def append_file(filename,data:bytes):
    import os.path
    from pathlib import Path

    with open(filename, "ab") as f:

        f.write(data)
