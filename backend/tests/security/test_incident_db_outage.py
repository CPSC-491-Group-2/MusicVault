
import os
import shutil
import subprocess
import time
import uuid

import pytest


def docker(*args):
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )



def wait_for_database(name):
    """
    Wait until the test database exists
    and can execute an SQL query.
    """
    for _ in range(45):
        result = docker(
            "exec", name,
            "psql",
            "-U", "incident_user",
            "-d", "incident_test",
            "-t", "-A",
            "-c", "SELECT 1;",
        )

        if (
            result.returncode == 0
            and result.stdout.strip() == "1"
        ):
            return True

        time.sleep(1)

    return False



@pytest.mark.skipif(
    os.getenv("MV_RUN_DB_OUTAGE") != "1",
    reason="Database outage drill requires explicit opt-in",
)
def test_database_outage_and_recovery():
    assert shutil.which("docker"), "Docker is required"

    # Unique disposable container, never a team database.
    name = f"mv-soc2-drill-{uuid.uuid4().hex[:12]}"

    try:
        result = docker(
            "run", "-d",
            "--name", name,
            "--network", "none",
            "-e", "POSTGRES_USER=incident_user",
            "-e", "POSTGRES_PASSWORD=local_simulation_only",
            "-e", "POSTGRES_DB=incident_test",
            "postgres:16",
        )

        assert result.returncode == 0, result.stderr
        assert wait_for_database(name), "Database did not start"

        # Create sample data before the outage.
        result = docker(
            "exec", name,
            "psql", "-v", "ON_ERROR_STOP=1",
            "-U", "incident_user",
            "-d", "incident_test",
            "-c",
            "CREATE TABLE recovery_check (id INT PRIMARY KEY); "
            "INSERT INTO recovery_check VALUES (1);",
        )
        assert result.returncode == 0, result.stderr

        # Simulate outage.
        result = docker("stop", name)
        assert result.returncode == 0, result.stderr

        # Verify incident detection.
        result = docker(
            "inspect", "--format",
            "{{.State.Running}}", name,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "false"

        # Restore service.
        result = docker("start", name)
        assert result.returncode == 0, result.stderr
        assert wait_for_database(name), "Recovery failed"

        # Verify existing data survived the outage.
        result = docker(
            "exec", name,
            "psql", "-t", "-A",
            "-U", "incident_user",
            "-d", "incident_test",
            "-c", "SELECT id FROM recovery_check;",
        )

        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "1"

    finally:
        # Remove only the uniquely named simulation
        # container and its anonymous volumes.
        docker("rm", "-f", "-v", name)
