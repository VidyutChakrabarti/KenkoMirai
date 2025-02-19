#!/bin/bash
# This script deploys the Kubernetes manifests

kubectl apply -f ../k8s/deployment.yaml
kubectl apply -f ../k8s/service.yaml
echo "Deployment initiated."
