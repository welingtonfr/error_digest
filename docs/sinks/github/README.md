# Sink: GitHub

> **Status:** planned. `GithubSink` (`src/error_digest/sinks/github_sink.py`) is only a skeleton; `write` and `comment` do nothing yet.

Intended configuration (from `config-dev.yaml`, may change when implemented):

```yaml
sinks:
  - type: github
    repo: my-org/my-app
    pat_token: GITHUB_TOKEN     # name of the env var holding the token
```

Intended behavior: create one issue per error group (`write`) and add a comment to an existing issue when the same error shows up again (`comment`).
