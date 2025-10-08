#!/usr/bin/env python3

"""
Simple autoinstall validator that works with Python 3.10
Uses only the legacy validation method without importing complex subiquity modules
"""

import argparse
import json
import sys
import yaml
import jsonschema

def parse_cloud_config(data: str) -> dict:
    """Parse cloud-config and extract autoinstall data."""
    lines = data.splitlines()
    # Handle YAML document separator at the beginning
    if lines[0] == "---":
        lines = lines[1:]

    if not lines[0] == "#cloud-config":
        raise AssertionError(
            "Expected data to be wrapped in cloud-config "
            "but first line is not '#cloud-config'. Try "
            "passing --no-expect-cloudconfig."
        )

    # Rejoin the lines without the YAML separator
    cleaned_data = "\n".join(lines)
    cc_data = yaml.safe_load(cleaned_data)

    if "autoinstall" not in cc_data:
        raise AssertionError(
            "Expected data to be wrapped in cloud-config "
            "but could not find top level 'autoinstall' key."
        )
    return cc_data["autoinstall"]

def parse_autoinstall(user_data: str, expect_cloudconfig: bool) -> dict:
    """Parse stringified user_data and extract autoinstall data."""
    if expect_cloudconfig:
        return parse_cloud_config(user_data)
    else:
        return yaml.safe_load(user_data)

def legacy_verify(ai_data: dict, schema_file: str) -> None:
    """Legacy verification method using JSON schema"""
    # support top-level "autoinstall" in regular autoinstall user data
    if "autoinstall" in ai_data:
        data = ai_data["autoinstall"]
    else:
        data = ai_data

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    jsonschema.validate(data, schema)

def main():
    parser = argparse.ArgumentParser(
        description="Simple autoinstall validator for Python 3.10"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the user data instead of stdin",
        type=argparse.FileType("r"),
        default=sys.stdin,
    )
    parser.add_argument(
        "--no-expect-cloudconfig",
        dest="expect_cloudconfig",
        action="store_false",
        help="Assume the data is not wrapped in cloud-config.",
        default=True,
    )
    parser.add_argument(
        "--json-schema",
        help="Path to JSON schema file",
        default="autoinstall-schema.json",
    )

    args = parser.parse_args()

    try:
        user_data = args.input.read()
        ai_data = parse_autoinstall(user_data, args.expect_cloudconfig)
        legacy_verify(ai_data, args.json_schema)
        print("Success: The provided autoinstall config validated successfully")
        return 0
    except Exception as exc:
        print(f"Failure: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())