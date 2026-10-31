
"""
SOC 2 Incident Management Simulation A

Scenario:
A developer accidentally exposes a credential.

Safety:
- Generates only a synthetic credential.
- Uses a temporary directory.
- Never connects to Spotify or Supabase.
- Never modifies the Git repository.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


GITLEAKS = shutil.which("gitleaks")

# Construct the canary during execution rather than
# placing the complete secret-like string in Git.
CANARY_PREFIX = "MV_SIMULATION_NOT_REAL_"
CANARY_SUFFIX = "12345"


@pytest.mark.skipif(
    GITLEAKS is None,
    reason="Gitleaks is not installed"
)
def test_fake_credential_incident_detection():

    fake_credential = (
        CANARY_PREFIX + CANARY_SUFFIX
    )

    config = r"""
title = "MusicVault Incident Simulation"

[[rules]]
id = "musicvault-synthetic-secret"
description = "Detect fake MusicVault credentials"
regex = '''MV_SIMULATION_NOT_REAL_[A-Za-z0-9]+'''
keywords = ["MV_SIMULATION_NOT_REAL_"]
"""

    with tempfile.TemporaryDirectory() as tmp:
        test_dir = Path(tmp)

        config_path = test_dir / "gitleaks-test.toml"
        config_path.write_text(config, encoding="utf-8")

        fake_file = test_dir / "simulated-config.txt"
        fake_file.write_text(
            f"TEST_TOKEN={fake_credential}\n",
            encoding="utf-8",
        )

        # Phase 1: Detect the simulated leak.
        detection = subprocess.run(
            [
                GITLEAKS,
                "dir",
                str(fake_file),
                "--config",
                str(config_path),
                "--redact",
                "--exit-code",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert detection.returncode == 1, (
            "Expected the fake secret to be detected. "
            f"Scanner exit code: {detection.returncode}"
        )

        # Phase 2: Contain the simulated incident.
        fake_file.write_text(
            "TEST_TOKEN=REMOVED\n",
            encoding="utf-8",
        )

        # Phase 3: Verify recovery.
        recovery = subprocess.run(
            [
                GITLEAKS,
                "dir",
                str(fake_file),
                "--config",
                str(config_path),
                "--redact",
                "--exit-code",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert recovery.returncode == 0, (
            "Expected the corrected file to pass scanning. "
            f"Scanner exit code: {recovery.returncode}"
        )
