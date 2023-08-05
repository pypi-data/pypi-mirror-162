import sys


def note(msg: str) -> None:
    """Print a message stdout and flush"""
    print(f"{msg}", file=sys.stdout, flush=True)


def warn(msg: str) -> None:
    """Print a warning to stderr and flush"""
    print(f"warning: {msg}", file=sys.stderr, flush=True)


def die(msg: str) -> None:
    """Print an error and exit"""
    print(f"error: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)