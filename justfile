# ==========================================
# Justfile — Build Automation for audio-vault
# ==========================================

PROJECT_NAME := "audio-vault"
BIN_DIR := "bin"
BIN := BIN_DIR + "/" + PROJECT_NAME + ".exe"
INSTALL_DIR := "$env:LOCALAPPDATA/Programs/" + PROJECT_NAME
set shell := ["powershell.exe", "-NoProfile", "-c"]

default: build_run

build:
    @echo "Building {{PROJECT_NAME}}..."
    @if (-not (Test-Path {{BIN_DIR}})) { New-Item -ItemType Directory -Force {{BIN_DIR}} | Out-Null }
    @go build -o {{BIN}} ./cmd/{{PROJECT_NAME}}
    @echo "Build complete: {{BIN}}"

run:
    @echo "Running {{PROJECT_NAME}}..."
    @& ".\{{BIN}}"

build_run: build run

clean:
    @echo "Cleaning build artifacts..."
    @if (Test-Path {{BIN_DIR}}) { Remove-Item -Recurse -Force {{BIN_DIR}} }
    @echo "Clean complete"

deps:
    @echo "Tidying Go modules..."
    @go mod tidy
    @echo "Dependencies updated"
