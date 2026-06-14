#!/usr/bin/env bash
# Start minikube and deploy the full WealthMesh stack.
# Hardware: RTX 2050 (4GB VRAM) — Ollama runs on host, not in k8s.
set -euo pipefail

PROFILE="${MINIKUBE_PROFILE:-wealthmesh}"
CPUS="${MINIKUBE_CPUS:-4}"
MEMORY="${MINIKUBE_MEMORY:-6144}"   # 6 GB — leaves room for Ollama on host

echo "==> Starting minikube profile: $PROFILE"
minikube start \
  --profile "$PROFILE" \
  --cpus "$CPUS" \
  --memory "${MEMORY}mb" \
  --driver docker \
  --kubernetes-version v1.30.0 \
  --addons ingress,metrics-server

echo "==> Pointing Docker daemon to minikube"
eval "$(minikube docker-env --profile "$PROFILE")"

echo "==> Building service images inside minikube"
SERVICES=(orchestrator agent-financial agent-market agent-docs agent-action agent-qa voice)
for svc in "${SERVICES[@]}"; do
  echo "  Building wealthmesh/$svc:dev ..."
  docker build \
    -f "services/$svc/Dockerfile" \
    -t "wealthmesh/$svc:dev" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .
done

echo "==> Adding wealthmesh.local to /etc/hosts (requires sudo)"
MINIKUBE_IP=$(minikube ip --profile "$PROFILE")
if ! grep -q "wealthmesh.local" /etc/hosts; then
  echo "$MINIKUBE_IP wealthmesh.local" | sudo tee -a /etc/hosts
fi

echo "==> Deploying with Helm (dev values)"
helm upgrade --install wealthmesh helm/wealthmesh \
  --namespace wealthmesh \
  --create-namespace \
  --set global.imagePullPolicy=Never \
  --set images.orchestrator.tag=dev \
  --set images.agentFinancial.tag=dev \
  --set images.agentMarket.tag=dev \
  --set images.agentDocs.tag=dev \
  --set images.agentAction.tag=dev \
  --set images.agentQa.tag=dev \
  --set images.voice.tag=dev \
  --wait --timeout 5m

echo ""
echo "==> WealthMesh is up!"
echo "    API:       http://wealthmesh.local/api"
echo "    Keycloak:  http://wealthmesh.local/auth"
echo "    Dashboard: kubectl -n wealthmesh get pods"
echo ""
echo "    To stop: minikube stop --profile $PROFILE"
echo "    To delete: minikube delete --profile $PROFILE"
