# Security Policy

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Microsoft takes the security of our software products and services seriously, including all source
code repositories managed through our GitHub organizations.

If you believe you have found a security vulnerability in this repository, please report it to us
through coordinated disclosure:

- Visit the [Microsoft Security Response Center (MSRC)](https://msrc.microsoft.com/create-report)
- Email [secure@microsoft.com](mailto:secure@microsoft.com)

Please include as much of the following information as possible to help us better understand and
resolve the issue:

- Type of issue (e.g. hardcoded credential, insecure dependency, injection vulnerability)
- Full path of the affected source file(s)
- Location of the affected source code (tag, branch, commit, or direct URL)
- Steps required to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

You should receive a response within 24 hours. If for some reason you do not, please follow up via
email to ensure we received your original message.

For more information, see the [Microsoft Security Response Center FAQ](https://www.microsoft.com/en-us/msrc/faqs-report-a-vulnerability).

## Supported Versions

This repository contains demo code. We address security issues on the `main` branch only.

## Credential Safety

This repository uses `DefaultAzureCredential` via the Azure Identity SDK — **no API keys or secrets
are required in code**. Never commit `.env` files; the `.gitignore` already excludes them. If you
accidentally push credentials, rotate them immediately and contact the MSRC as above.
