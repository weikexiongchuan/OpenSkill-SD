---
name: autodl-host-facts-collect
description: Atomic capability skill for collecting host facts from an AutoDL server. Use for one-shot capture of OS, GPU, storage, mount, and `screen` session state.
---

# AutoDL Host Facts Collect

## Purpose
Capture a host snapshot that can be reviewed before deeper operations.

## Capabilities
- Record OS and hostname details.
- Record GPU visibility through `nvidia-smi`.
- Record storage, mounts, and `screen` sessions.

## Typical Inputs
- Optional output file path

## Typical Outputs
- Host facts log file

## Route
- Use this before remote workspace planning or service deployment when host facts are missing.

## Load On Demand
- `references/field-validated-notes.md`
