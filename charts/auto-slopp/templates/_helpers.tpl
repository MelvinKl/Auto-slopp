{{/*
Expand the name of the chart.
*/}}
{{- define "auto-slopp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "auto-slopp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "auto-slopp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "auto-slopp.labels" -}}
helm.sh/chart: {{ include "auto-slopp.chart" . }}
{{ include "auto-slopp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "auto-slopp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "auto-slopp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "auto-slopp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "auto-slopp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate init container command for installing additional programs
*/}}
{{- define "auto-slopp.initContainer.command" -}}
{{- if .Values.additionalPrograms }}
- /bin/sh
- -c
- |
  apt-get update && \
  apt-get install -y --no-install-recommends {{ join " " .Values.additionalPrograms }} && \
  rm -rf /var/lib/apt/lists/*
{{- end }}
{{- end }}
