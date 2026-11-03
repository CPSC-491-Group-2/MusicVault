import subprocess
import sys


def test_pytest_detects_controlled_failure(tmp_path):
    """Pytest must report a nonzero result when application behavior is broken."""

    failing_test = tmp_path / "test_controlled_failure.py"

    failing_test.write_text(
        """
def test_controlled_failure():
    assert 1 == 2
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(failing_test),
            "-q",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    print("Controlled negative-test output:")
    print(output)

    assert result.returncode != 0
    assert "1 failed" in output.lower()