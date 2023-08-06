import sys
from .pyncdu import pyncdu


if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except:
        path = "."
    pyncdu(path)
