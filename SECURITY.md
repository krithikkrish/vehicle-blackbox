# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

---

## 🔒 Reporting a Vulnerability

We take the security of embedded hardware and telemetry endpoints seriously.

If you discover a security vulnerability or sensitive credential exposure:
1. **Do not create a public GitHub issue.**
2. Report the vulnerability privately via [GitHub Private Vulnerability Reporting](https://github.com/krithikkrish/vehicle-blackbox/security/advisories/new) or contact the repository owner.
3. Include detailed steps to reproduce the issue and any relevant system logs.

We will review the report and coordinate a patch promptly.

---

## 🛡️ Telemetry & Secret Handling

- **Never commit real cellular phone numbers or private API credentials** to source control.
- Always use the `.env.example` template and configure local numbers via environment variables (`EMERGENCY_PHONE`).
- `.env` and `*.log` files are automatically excluded via `.gitignore`.
