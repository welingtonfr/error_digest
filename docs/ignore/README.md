# Ignore

A list of rules to **drop errors** before grouping. Dropped errors do not count toward the totals and do not take a slot in `max_issues`.

```yaml
ignore:
  - 'Connection reset by peer'
  - 're:timeout after \d+ms'
```

## Rule types

| Rule | How it matches |
|---|---|
| Plain text | The message **contains** the text, case-insensitive. |
| `re:<regex>` | The regex is found **anywhere** in the message (`re.search`), case-insensitive. |

Examples:

| Rule | Message | Dropped? |
|---|---|---|
| `Connection reset by peer` | `read: connection RESET by peer` | yes |
| `re:timeout after \d+ms` | `GET /x failed: Timeout after 3000ms` | yes |
| `Error (code 5)` | `Error (code 5)` | yes (literal text) |
| `Error (code 5)` | `Error code 5` | no |

## Caveats

- **Plain text is not a regex.** Parentheses, dots and other symbols are literal. It only becomes a regex with the `re:` prefix.
- **Use single quotes in YAML** for regexes. In double quotes, `\d` would be treated as an escape by YAML. In single quotes the backslash is kept as is.
- **An invalid regex prevents the program from starting**, with `Invalid ignore regex 're:(': ...`, instead of failing in the middle of a run.
- Empty rules are ignored. A missing or empty section is `[]`.
- The filter looks only at the log **message**, not at the labels.

## Not implemented yet

`scrub` (sensitive data removal) and `state` (remembering what was already reported) appear commented out in `config-dev.yaml`, but have no code yet.
