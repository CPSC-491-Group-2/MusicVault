#verifying that security scvanner correctly detects a simulatated credential exposure 
import subprocess
import tempfile
from pathlib import Path


def test_synthetic_secret_is_detected():
    # This test requires Gitleaks to be installed in CI.
    config = """
title = "MusicVault Simulation"

[[rules]]
id = "musicvault-canary"
description = "Synthetic incident test credential"
regex = '''MV_SIMULATION_NOT_REAL_[A-Za-z0-9]+'''
keywords = ["MV_SIMULATION_NOT_REAL_"]
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        folder = Path(temp_dir)

        (folder / "gitleaks.toml").write_text(config)

        # Fake credential, never a real API key.
        test_file = folder / "simulated-secret.txt"
        test_file.write_text(
            "MV_SIMULATION_NOT_REAL_12345"
        )

        result = subprocess.run(
            [
                "gitleaks",
                "dir",
                str(folder),
                "--config",
                str(folder / "gitleaks.toml"),
                "--redact",
                "--exit-code",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        # A detected secret produces exit code 1.
        assert result.returncode == 1

        # Remove the simulated leak.
        test_file.unlink()

        clean_result = subprocess.run(
            [
                "gitleaks",
                "dir",
                str(folder),
                "--config",
                str(folder / "gitleaks.toml"),
                "--redact",
                "--exit-code",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert clean_result.returncode == 0
