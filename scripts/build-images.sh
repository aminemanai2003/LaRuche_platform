#!/usr/bin/env bash
# Build all service Docker images locally (without minikube).
# Usage: ./scripts/build-images.sh [tag]
set -euo pipefail

TAG="${1:-latest}"
SERVICES=(orchestrator agent-financial agent-market agent-docs agent-action agent-qa voice)

for svc in "${SERVICES[@]}"; do
  echo "Building wealthmesh/$svc:$TAG ..."
  docker build \
    -f "services/$svc/Dockerfile" \
    -t "wealthmesh/$svc:$TAG" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .
  echo "  done: wealthmesh/$svc:$TAG"
done

echo ""
echo "All images built. To push:"
echo "  for img in orchestrator agent-financial agent-market agent-docs agent-action agent-qa voice; do"
echo "    docker push wealthmesh/\$img:$TAG"
echo "  done"
