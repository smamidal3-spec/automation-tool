# Design Decisions

## ruamel.yaml over plain PyYAML
Used to preserve YAML style and reduce noisy formatting diffs in pull requests.

## Service Layer Separation
`app/services` modules isolate policy, provider, and patch logic so endpoint handlers remain orchestration-focused and testable.

## Dry-Run by Default
Defaulting to dry-run minimizes accidental mass changes while operators validate behavior.
