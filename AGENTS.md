# Repository instructions

## Development environment

- Keep PyPy and Codon in one Dev Container image. They share the same OS
  dependencies, editor extensions, workspace, and AtCoder tooling.
- Build the container directly from `.devcontainer/Dockerfile` through
  `.devcontainer/devcontainer.json`.
- Do not introduce Docker Compose while the development environment consists
  of a single container. Reconsider Compose only when independent supporting
  services, networks, or volumes are required.
- Keep runtime-specific libraries separate. PyPy packages belong in the PyPy
  installation and PyPy-specific source helpers belong under `pypy/`. Packages
  used by Codon through CPython and Codon-specific source helpers belong under
  `codon/`.
- Keep shared tools, including `online-judge-tools`, and shared VS Code
  extensions configured once in the common image or Dev Container definition.
- Order Dockerfile layers to keep rebuilds fast: put expensive, stable runtime
  installation steps before tools and runtime-specific package lists that
  change more often. When adding or moving a step, consider which later layers
  its changes would invalidate.
- Preserve existing comments, including commented-out code and package lists,
  even when removing them would not change runtime behavior. Comments may
  document intent, alternatives, or environment inventories; do not delete or
  rewrite them without explicit user approval.

## Verification

- After changing Dev Container configuration, validate
  `.devcontainer/devcontainer.json` and check that all referenced files exist.
- When Docker is available, build the image and verify that `pypy3`, `codon`,
  `oj`, and `oj-api` are all available in the same container.
- Verify both `pypy/run.sh` and `codon/run.sh` when changing runtime setup or
  dependencies.
