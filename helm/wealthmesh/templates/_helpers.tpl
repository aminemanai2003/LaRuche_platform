{{/*
Expand the name of the chart.
*/}}
{{- define "wealthmesh.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "wealthmesh.labels" -}}
helm.sh/chart: {{ include "wealthmesh.name" . }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service deployment template
*/}}
{{- define "wealthmesh.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  namespace: {{ $.Release.Namespace }}
  labels:
    app: {{ .name }}
    {{- include "wealthmesh.labels" $ | nindent 4 }}
spec:
  replicas: {{ .replicas | default 1 }}
  selector:
    matchLabels:
      app: {{ .name }}
  template:
    metadata:
      labels:
        app: {{ .name }}
    spec:
      containers:
        - name: {{ .name }}
          image: {{ .image }}
          imagePullPolicy: {{ $.Values.global.imagePullPolicy }}
          ports:
            - containerPort: {{ .port }}
          envFrom:
            - configMapRef:
                name: wealthmesh-env
            - secretRef:
                name: wealthmesh-secrets
          readinessProbe:
            httpGet:
              path: /health
              port: {{ .port }}
            initialDelaySeconds: 5
            periodSeconds: 10
          resources: {{- toYaml $.Values.resources.default | nindent 12 }}
{{- end }}
