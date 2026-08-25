<div align="center">

# Kenko Prototype Boundary

### Preserved experiments outside the supported runtime

<p>
  <a href="../README.md"><img alt="Open canonical project" src="https://img.shields.io/badge/OPEN-CANONICAL_PROJECT-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
  <a href="../docs/architecture.md"><img alt="View architecture" src="https://img.shields.io/badge/VIEW-ARCHITECTURE-B8E7D1?style=for-the-badge&labelColor=101815&color=477A65"></a>
</p>

</div>

---

This directory contains alternate Flask/Next experiments with contracts that differ from the supported application. It is intentionally excluded by `.dockerignore`, Docker Compose, Kubernetes, CI, and the root npm workspace.

Production and development work should use:

- `../backend/`
- `../frontend/`
- `../ml/`

These experiments remain available for selective reference; do not run them alongside the supported stack because ports, state models, and API semantics are incompatible.
