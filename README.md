# LEON-SOPHIA Dual-Agent Reasoning System

A structured framework for high-quality decision-making through adversarial collaboration between two specialized AI agents.

## Agents

| Agent | Role | Disposition |
|-------|------|-------------|
| **LEON** | Strategic planner, architect, forward-thinker | Constructive, generative |
| **SOPHIA** | Critic, bias-detector, ethics governor | Skeptical, adversarial |

## Core Philosophy
No plan, design, or decision is accepted until it has survived SOPHIA's challenge. LEON builds; SOPHIA breaks. The synthesis layer reconciles their outputs into a final, high-confidence result.

## Directory Structure

```
leon-sophia-system/
├── agents/         # Per-agent identity, mission, and protocols
├── shared/         # Shared standards, memory, and context rules
├── synthesis/      # Arbitration, debate, and final decision logic
├── workflows/      # End-to-end task workflows
├── tests/          # Validation and stress-test suites
└── templates/      # Output scaffolding for each agent and joint work
```

## Getting Started
1. Read `system_manifest.yaml` for the system version and configuration.
2. Load agent identities from `agents/LEON/identity.md` and `agents/SOPHIA/identity.md`.
3. Select the appropriate workflow from `workflows/` for your task type.
4. Follow the workflow; outputs populate into `templates/`.
