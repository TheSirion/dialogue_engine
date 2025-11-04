#!/usr/bin/env python3
"""
Wrapper script to run the dialogue engine example with proper environment setup.
"""

import sys
import os
from pathlib import Path


def setup_environment():
    """Setup the Python path to include the current directory"""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()

    # Add the script directory to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
        print(f"Added {script_dir} to Python path")

    # Also add the parent directory if needed
    parent_dir = script_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
        print(f"Added {parent_dir} to Python path")

    return script_dir


def main():
    """Main function to run the example"""
    print("Setting up environment...")
    script_dir = setup_environment()

    try:
        # Now import and run the actual example
        import example_usage

        print("Successfully imported example_usage")
        example_usage.main()
    except Exception as e:
        print(f"Error running example: {e}")
        print("Make sure you're running this from the dialogue_engine directory")
        print("Usage: python run_example.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
