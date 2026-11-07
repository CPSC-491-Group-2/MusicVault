# VM-01 — Dependency Vulnerability Scanning

## SOC 2 Alignment
- **Criterion:** CC7.1 — System Operations
- **Control:** VM-01 — Dependency Vulnerability Scanning
- **Application:** MusicVault
- **Scope:** Flask backend Python dependencies

## Control Objective
Identify known security vulnerabilities in third-party dependencies and ensure identified vulnerabilities are reviewed, documented, and remediated appropriately.

## Testing Tool
The project uses `pip-audit` to analyze Python dependencies against known vulnerability advisory databases.

## Testing Procedure

1. Activate the project's Python virtual environment.
2. Execute `pip-audit` against `backend/requirements.txt`.
3. Generate a JSON vulnerability report.
4. Review reported vulnerabilities.
5. Document findings and determine necessary remediation.
6. Repeat the scan after applying fixes.

## Local Execution

Install the scanner:

```powershell
python -m pip install pip-audit
```

Run the scan:

```powershell
python -m pip_audit -r backend/requirements.txt
```

Generate a JSON report:

```powershell
python -m pip_audit -r backend/requirements.txt --format json --output docs/security/pip-audit/reports/vm01-backend.json
```

## Acceptance Criteria

- The dependency scan completes successfully.
- Direct and resolvable transitive dependencies are evaluated.
- Known vulnerabilities are identified and documented.
- No known vulnerabilities remain unaddressed without approved risk acceptance.
- Scan evidence is retained for review.
- Remediation is verified by repeating the scan.

## Initial Test Results

**Date:** November 2, 2026

- Dependencies scanned: 21
- Known vulnerabilities detected: 0
- Initial scan result: Passed
- Report: `reports/vm01-backend.json`

## Evidence Collection

Local reports are generated in the `reports/` directory. Automated CI reports will be retained as GitHub Actions artifacts once the workflow is implemented.

## Limitations

Dependency scanning detects known vulnerabilities in the scanned dependency set. It does not replace source code analysis, dynamic application security testing, or vulnerability testing of application logic.

Unpinned dependencies may resolve to different versions on subsequent scans. Results must be interpreted in relation to the actual dependency versions used by the application.