#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from pathlib import Path

from main import main


def parse_args():
    parser = argparse.ArgumentParser(
        description="Redrob Intelligent Candidate Ranking Engine"
    )

    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl"
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Output CSV filename"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    if not Path(args.candidates).exists():
        print(f"Dataset not found: {args.candidates}")
        sys.exit(1)

    os.environ["CANDIDATES_PATH"] = args.candidates
    os.environ["OUTPUT_PATH"] = args.out

    main()

    print(f"\nSubmission generated successfully: {args.out}")