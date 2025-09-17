# AGENTS.md — Working Context for `xmltodict`

This page gives coding agents only what they need to contribute safely and quickly. For full API details, examples, and edge‑case discussion, defer to the README.

---

## 1) What `xmltodict` is
A single‑file Python library that converts **XML ↔ dict**, making XML feel like JSON for most practical use cases. It aims for clarity and convenience over perfect round‑tripping of every XML nuance.

---

## 2) Core surface area
- **Module**: `xmltodict.py` (single file)
- **Primary functions**:
  - `parse(xml_input, **kwargs)` → `dict`
  - `unparse(input_dict, **kwargs)` → `str`/bytes
- **Options agents commonly need**:
  - Parsing: `process_namespaces`, `namespaces`, `force_list`, `force_cdata`, `item_depth` + `item_callback` (streaming), `process_comments`, `attr_prefix` (default `@`), `cdata_key` (default `#text`), `strip_whitespace`, `disable_entities` (default **True**)
  - Unparsing: `pretty`, `short_empty_elements`, `expand_iter`, `full_document`, `encoding`

---

## 3) Streaming guidance
For large XML, use **streaming** with `item_depth` + `item_callback`. Expect constant memory relative to item size, not whole‑document size. Keep callbacks fast and side‑effect‑free.

---

## 4) Security posture
- **Entity expansion is disabled by default** (`disable_entities=True`).
- **Input validation**: element/attribute names are validated and reject illegal characters (e.g., `<`, `>`, `/`, quotes, `=`, whitespace) and disallowed starts (e.g., `?`, `!`).
- **Reminder for agents**: do not relax security defaults unless tests cover your change.

---

## 5) Known caveats / non‑goals
- Exact **mixed content** ordering and **attribute order** are not guaranteed to be preserved.
- Comment handling is best‑effort; don’t rely on multiple top‑level comments round‑tripping in exact order.
- The project prioritizes common XML→dict workflows over exhaustive XML edge‑cases.

---

## 6) Project conventions (how to contribute changes)
- **Python**: 3.9+.
- **Commits**: Conventional Commits (`type(scope?): subject`).
- **Tests**: `pytest` (usually via `tox`). All new behavior must have tests; include edge cases and failure paths.
- **CI/CD**: GitHub Actions runs tox; releases are automated (Release Please + GitHub Release → PyPI).
- **Types**: Optional stub package `types-xmltodict` is available for type checkers.

---

## 7) Minimal repo map
```
xmltodict/
├── xmltodict.py          # Library (single file)
├── tests/                # Test suite
│   ├── test_xmltodict.py # XML→dict
│   └── test_dicttoxml.py # dict→XML
├── .github/workflows/    # CI/release automation
├── pyproject.toml        # Packaging/config (or equivalent)
└── README.md             # Authoritative API + examples
```

---

## 8) Agent checklists
### Adding/changing behavior
- [ ] Write or update tests first (success + failure cases).
- [ ] Preserve security defaults; document any opt‑outs.
- [ ] Keep kwargs names/backwards compatibility unless a major bump is justified.
- [ ] Update README only if public API changes.

### Performance changes
- [ ] Benchmark on representative large XML (streaming when applicable).
- [ ] Avoid unbounded growth in intermediate structures.

### Release readiness
- [ ] All tests pass locally and in CI across supported Pythons.
- [ ] Conventional commit message(s) are in place for changelog generation.

---

## 9) Pointers
- **README**: canonical API and usage.
- **Issues/PRs**: prior discussions on namespaces, streaming, and comment handling.
- **Type Stubs**: `types-xmltodict` on PyPI.
