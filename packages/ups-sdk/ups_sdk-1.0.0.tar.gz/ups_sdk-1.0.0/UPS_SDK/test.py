VERSION = {}


with open("./__init__.py") as fp:
    exec(fp.read(), VERSION)

