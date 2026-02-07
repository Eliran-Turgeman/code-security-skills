$ErrorActionPreference = 'Stop'

if (-not (Test-Path -Path "./out")) {
  New-Item -ItemType Directory -Force -Path "./out" | Out-Null
}

$jobs = @()

$jobs += Start-Job {
  docker run --rm -v "${PWD}:/repo:ro" -v "${PWD}/out:/out" zricethezav/gitleaks:latest dir /repo --report-path /out/gitleaks.json
}

$jobs += Start-Job {
  docker run --rm -v "${PWD}:/repo:ro" -v "${PWD}/out:/out" semgrep/semgrep:latest semgrep scan --config auto --json --json-output=/out/semgrep.json /repo
}

$jobs += Start-Job {
  docker run --rm -v "${PWD}:/repo:ro" -v "${PWD}/out:/out" ghcr.io/google/osv-scanner:latest scan --format json --output /out/osv.json /repo
}

$jobs += Start-Job {
  docker run --rm -v "${PWD}:/repo:ro" -v "${PWD}/out:/out" aquasec/trivy:latest config --format json --output /out/trivy.json /repo
}

$jobs | Wait-Job | Receive-Job | Out-Null
$jobs | Remove-Job | Out-Null
