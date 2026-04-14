# -*- coding: utf-8 -*-
from engine_runner import configure_logging, run_engine


def main():
    configure_logging()
    return run_engine()


if __name__ == "__main__":
    raise SystemExit(main())
