from __future__ import annotations

import argparse

from .cli import process_results_cli, run_cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MBA RAG package entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run", help="Run experiments from a YAML config.")
    subparsers.add_parser("process-results", help="Process structured or legacy results into reports.")
    args, remaining = parser.parse_known_args(argv)

    if args.command == "run":
        return run_cli(remaining)
    return process_results_cli(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
