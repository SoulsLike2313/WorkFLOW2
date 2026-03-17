# Canonical Machine Protection Policy

## Purpose

Protect canonical machine authority and prevent external helper nodes from mutating protected governance/canonical layers.

## Protected Zones

- governance core in `docs/governance/`
- canonical manifests in `workspace_config/`
- canonical acceptance and transition artifacts

## Rules

- creator authority required for final canonical acceptance
- external helper output must pass integration inbox review
- helper nodes cannot grant themselves canonical rights
- canonical machine must keep integration as explicit admission gate

## Forbidden External Actions

- direct merge to canonical state without creator decision
- changing protected governance documents as part of helper block unless explicitly scoped and reviewed
- bypassing integration inbox routing

## Recovery

If external package attempts protected-zone mutation outside contract:

1. quarantine package
2. log incident
3. keep canonical branch unchanged
4. require explicit creator review

