#!/usr/bin/env python3

import os
from pathlib import Path
from unittest.mock import patch
from settings.main import Settings

print("=== Debug Test ===")

# Test 1: Default behavior
print("\n1. Default behavior:")
s1 = Settings()
print(f"   cli_configurations length: {len(s1.cli_configurations)}")
if s1.cli_configurations:
    print(f"   First config: {s1.cli_configurations[0].cli_command}")

# Test 2: With explicit env var for config file pointing to our default
print("\n2. With AUTO_SLOPP_CONFIG_FILE=config/default.yaml:")
os.environ["AUTO_SLOPP_CONFIG_FILE"] = "config/default.yaml"
s2 = Settings()
print(f"   cli_configurations length: {len(s2.cli_configurations)}")
if s2.cli_configurations:
    print(f"   First config: {s2.cli_configurations[0].cli_command}")
del os.environ["AUTO_SLOPP_CONFIG_FILE"]

# Test 3: Clear environment and try to load from file
print("\n3. Clear env, then load from file:")
env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_")}
print(f"   Vars to clear: {list(env_vars_to_clear.keys())}")
with patch.dict(os.environ, {}, clear=False):
    for key in env_vars_to_clear:
        if key in os.environ:
            del os.environ[key]
    s3 = Settings()
    print(f"   cli_configurations length: {len(s3.cli_configurations)}")
    if s3.cli_configurations:
        print(f"   First config: {s3.cli_configurations[0].cli_command}")

print("\n=== End Debug Test ===")