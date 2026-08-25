#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
manifest_dir="${script_dir}/../k8s"

command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required" >&2; exit 1; }
kubectl apply -k "${manifest_dir}"
kubectl -n kenkomirai rollout status deployment/kenkomirai-backend --timeout=180s
kubectl -n kenkomirai rollout status deployment/kenkomirai-frontend --timeout=180s
