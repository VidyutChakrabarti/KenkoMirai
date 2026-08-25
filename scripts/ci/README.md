# CI checks

The GitHub Actions workflow intentionally performs dependency-free checks. It
does not install Python or Node packages and does not build container images.
This keeps pull-request feedback bounded and avoids treating an unavailable
package index or Docker daemon as an application failure.

The checks validate:

- Python syntax for backend application and test sources.
- Frontend package and lockfile alignment plus required gateway files.
- Compose service definitions and Dockerfile contracts.

Runtime tests, frontend lint/build, and image builds remain release or
developer-environment checks because they require external dependencies.