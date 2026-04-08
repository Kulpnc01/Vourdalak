# Vourdalak Agent Protocol | Autonomous Operational Guide

This document defines the deterministic interface for an AI Orchestrator to control the Vourdalak pipeline.

## 1. System Topology & Discovery
The Agent must first parse the following JSON maps to understand the environment:
- **Okhotnik Config:** `01_Hunt/Okhotnik/okhotnik_config.json` (Proxy settings, tool paths)
- **Smotrityel Config:** `01_Hunt/Smotrityel/smotrityel_config.json` (Pathing, filter thresholds)
- **Vault Database:** `01_Hunt/Okhotnik/Toolchain/Armory/armory_vault.json` (Available identities)

## 2. Deterministic Workflows

### Phase A: Identity Provisioning
If the Agent requires a new identity for a specific platform:
1.  Execute `python 01_Hunt/Okhotnik/Toolchain/Armory/provisioner.py` to acquire a temporary email.
2.  Store new credentials using the Vault Manager:
    `python 01_Hunt/Okhotnik/Toolchain/Armory/vault_manager.py --add [platform] [user] [pass]`

### Phase B: Target Acquisition (The Hunt)
To initiate OSINT harvesting:
1.  Ensure proxy status is correct in `okhotnik_config.json`.
2.  Launch the Okhotnik Core:
    `python 01_Hunt/Okhotnik/okhotnik_core.py`
    - Input 1: `Target_Name` (Use underscores for spaces).
    - Input 2: `Aliases/Data` (Comma-separated strings).

### Phase C: Multimodal Weaving (Normalization)
To generate the behavioral dossier:
1.  Ensure raw data or backups are present in `01_Hunt/Smotrityel/Raw/Hunt/Subject/[Target_Name]` or `01_Hunt/Input/[Target_Name]`.
2.  Execute the Smotrityel Engine:
    `python 01_Hunt/Smotrityel/smotrityel_core.py`
3.  Monitor STDOUT for `[DISCOVERY]` tags to identify new subject handles found during weaving.

## 3. Data Schema (Consumption)
Normalized output is located at: `02_Feed/Compendium/[Target_Name]/`.
The Agent should parse files with `.md` extensions and read the YAML frontmatter for:
- `psych_score`: Heuristic psychological density (0.0 - 10.0).
- `behavioral_state`: Physiological inference (STABLE, ELEVATED, BASELINE).
- `context_confidence`: Temporal proximity score (0.0 - 1.0).

## 4. Operational Safety
- **Stealth:** Always verify `proxy_settings.enabled == true` before Phase B.
- **Throttling:** Do not execute consecutive hunts without checking account cooldowns in the Vault.
- **Resource Cleanup:** The engine handles `_temp_extract` cleanup; do not manually delete folders during processing.

---
*End of Protocol.*
