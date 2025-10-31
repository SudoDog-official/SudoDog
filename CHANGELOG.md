# Changelog

All notable changes to SudoDog will be documented in this file.

## [0.2.0] - 2025-10-31

### 🎉 Major Features

- **Custom Docker Image Support** - Users can now use their own Docker images with `--image` flag
- **Anonymous Telemetry System** - Opt-in privacy-first analytics with Postgres backend
- **Resource Limits** - CPU and memory limits for Docker containers
- **Improved CLI** - Beautiful Rich-based interface with better error messages

### ✨ New Features

- Added `--image` flag to specify custom Docker images
- Added `--cpu-limit` flag for CPU resource constraints
- Added `--memory-limit` flag for memory resource constraints
- Added `sudodog telemetry` command group (enable, disable, status, info)
- Added MIT License with Telemetry Addendum
- Added Postgres database storage for telemetry events
- Added Vercel backend for telemetry collection

### 🐛 Bug Fixes

- Fixed Docker stats collection to handle missing system_cpu_usage
- Fixed Click argument parsing for commands with options
- Fixed regex pattern validation in blocker
- Improved error handling for invalid Docker images

### 📚 Documentation

- Added comprehensive telemetry documentation (PRIVACY.md, TELEMETRY.md)
- Added custom Docker image examples
- Updated README with telemetry section
- Added installation instructions for different methods

### 🔧 Technical Improvements

- Refactored Docker sandbox to support custom images
- Made resource limits optional (None = no limit)
- Improved telemetry UI with beautiful prompts
- Added database auto-creation on first telemetry event
- Silenced non-critical stats warnings

## [0.1.0] - 2025-10-30

### 🎉 Initial Release

- Basic Docker container isolation
- Namespace-based sandboxing
- Pattern-based threat detection
- Audit logging
- File rollback capabilities
- Background daemon for monitoring
- Real-time CPU and memory tracking
