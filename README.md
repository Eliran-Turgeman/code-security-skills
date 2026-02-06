# code-security-skills

A repository of deterministic, security scanning skills that standardize how agents run common scanners and normalize findings into a shared schema.

## Available skills

- `security-scan` - Run secrets, SAST, SCA, and IaC scans in parallel and render a unified report.

## Install

### Codex
Within Codex, run `$skill-installer install skill from https://github.com/Eliran-Turgeman/code-security-skills/tree/master/skills/security-scan`

## Invoke

### Codex
Run `$security-scan`

## Requirements

- Docker (for all scanners)
- Python 3 (for the reporting script)
