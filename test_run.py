#!/usr/bin/env python3
"""
Test run using the sample data
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Override the data path to use sample
os.environ['CANDIDATE_DATA_PATH'] = os.path.join(os.path.dirname(__file__), "assets", "candidates_sample.jsonl")

# Now import and run the main function from our main.py
from main import main

if __name__ == "__main__":
    main()
