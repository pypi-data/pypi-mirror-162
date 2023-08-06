# omnisolver-test-tools

## Purpose

This meta-package tracks versions of test tools (e.g. pytest) used in Omnisolver and it's official
plugins.
Therefore, it reduces the burden of maintaining such dependencies in each repository separately.

## Installation

You typically don't install `omnisolver-test-tools` manually. Instead, the package gets installed
whenever you install Omnisolver or one of its official plugins with `test` requirements, e.g. by
running

```bash
pip install omnisolver[test]
```

which is only useful if you plan to run tests or contribute to Omnisolver.
