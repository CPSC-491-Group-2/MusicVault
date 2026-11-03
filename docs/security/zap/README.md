# VM-03 — Dynamic Application Security Testing

## SOC 2 Alignment

- **Criterion:** CC7.1 — System Operations
- **Control:** VM-03 — Dynamic Application Security Testing
- **Application:** MusicVault
- **Testing Tool:** OWASP ZAP
- **Sprint:** Sprint 4
- **Scope:** Next.js frontend and reachable unauthenticated application endpoints

## Control Objective

Identify potential security vulnerabilities in MusicVault by performing dynamic security scans against the running application.

The control uses OWASP ZAP baseline scanning to analyze HTTP requests, responses, security headers, and information disclosure risks.

## Implementation

OWASP ZAP runs inside Docker and performs passive security analysis against MusicVault's locally hosted frontend.

The control will also be integrated into GitHub Actions to automate vulnerability detection, report generation, and evidence collection.

No application security fixes or configuration changes are included in the Sprint 4 implementation.

## Initial Testing Results

**Date:** November 2, 2026

| Metric | Development Scan | Production-Mode Scan |
|---|---:|---:|
| Passed checks | 53 | 56 |
| Warning categories | 15 | 12 |
| Fail-level findings | 0 | 0 |
| Scanner exit code | 2 | 2 |

Both scans completed and generated HTML and JSON reports.

Exit code 2 indicates that ZAP detected warning findings but no findings configured as failures.

The production-mode scan examined 57 URLs.

## Identified Security Findings

### Medium-Risk Findings

**1. Content Security Policy Header Not Set**

Affected responses do not include a Content Security Policy.

Recommended future action:
- Evaluate and implement an appropriate CSP.
- Restrict unauthorized script and resource loading.
- Verify compatibility with Next.js and Spotify integrations.

**2. Missing Anti-clickjacking Header**

Affected application pages lack explicit clickjacking protection.

Recommended future action:
- Evaluate `X-Frame-Options` or CSP `frame-ancestors`.
- Restrict unauthorized framing of application pages.

### Additional Findings Requiring Review

- X-Content-Type-Options header missing.
- X-Powered-By framework information disclosure.
- Permissions Policy header missing.
- Cross-Origin-Embedder-Policy header missing or invalid.
- Application error disclosure associated with `/api/auth/spotify/login`.
- Potential sensitive information in URL parameters.
- Cache-control and content storage observations.

The sensitive information in URL findings included ZAP-generated test values. Actual credential leakage has not been confirmed.

The Spotify authentication endpoint returned HTTP 500 during testing. Further investigation is required to determine whether this was caused by unavailable backend services or inappropriate error handling.

## Potential Engineering Changes

The following improvements are recommended for consideration during future development:

1. Implement a tested Content Security Policy.
2. Configure anti-clickjacking protection.
3. Add appropriate HTTP security headers.
4. Disable unnecessary framework disclosure headers.
5. Investigate Spotify authentication error handling.
6. Verify that credentials are never transmitted in URL query parameters.
7. Review caching behavior for authenticated and sensitive pages.
8. Assess whether additional cross-origin isolation protections are appropriate.

These recommendations represent potential engineering work, not fixes completed during Sprint 4.

## Sprint 4 Acceptance Criteria

- OWASP ZAP successfully scans the running MusicVault application.
- HTML and JSON security reports are generated.
- Security findings are reviewed and documented.
- Potential remediation work is identified.
- GitHub Actions automatically executes baseline scans.
- Scan reports are retained as downloadable CI artifacts.
- Scanner execution errors are distinguished from vulnerability warnings.

## Evidence Collection

Local reports are stored in:

`docs/security/zap/reports/`

Automated CI reports will be retained as GitHub Actions artifacts.

The repository will retain this documentation and the workflow configuration, while generated reports will be excluded from version control.

## Limitations

This implementation uses unauthenticated passive baseline scanning.

It does not comprehensively test authenticated application functionality, business-logic vulnerabilities, or backend API security.

The automated workflow uses a temporary development server. Results may differ from production-mode scans and should be labeled accordingly.

## Future Work

Potential future security work includes vulnerability remediation, authenticated scanning, additional API coverage, production deployment validation, and risk-based CI enforcement.