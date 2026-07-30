# Security Policy

## Supported versions

Security fixes are applied to the latest revision on the default branch. Until the project publishes versioned releases, older snapshots are not supported.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities involving arbitrary code execution, command injection, path traversal, credential exposure, unsafe archive extraction, dependency confusion, or disclosure of research participant data. Use the repository host's private security advisory feature or contact the maintainers privately.

Include the affected skill and script, a minimal reproduction, impact, platform, and suggested mitigation. Maintainers should acknowledge a complete report within seven days and coordinate disclosure after a fix is available.

## Research-code safety boundary

The repository includes workflows that may inspect or execute third-party research code. Treat cloned repositories, model files, datasets, notebooks, archives, and build scripts as untrusted. Use an isolated environment, expose no credentials, mount only the required workspace, inspect commands before execution, and obtain explicit approval before installing or running dependencies.

Never submit secrets, private datasets, unpublished participant data, or identifying logs in a vulnerability report.

