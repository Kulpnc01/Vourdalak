# Project Vourdalak | Behavioral Context & OSINT Orchestrator

Vourdalak is a modular intelligence architecture designed to automate the collection, normalization, and psychological profiling of digital subjects. It integrates high-fidelity OSINT harvesting (**Okhotnik**) with multimodal behavioral weaving (**Smotrityel/EgoWeaver**).

## Architecture

### 01_Hunt: Acquisition & Normalization
*   **Okhotnik (The Hunter):** Orchestrates a toolchain of OSINT scanners (Sherlock, Maigret, etc.) to harvest digital footprints.
*   **Smotrityel (The Watcher):** Ingests raw OSINT and User Backups (social, messaging, health). Weaves these threads into a "Golden Record" with enriched spatial and physiological context.
*   **EgoWeaver Core:** The behavioral engine powering the normalization phase, providing forensic anchoring and psychological scoring.

### 02_Feed: Intelligence Output
*   Standardized Markdown dossiers
*   **AI Media Processing:** Automated local audio transcription (Whisper) and image description (LLaVA).
*   **Sequence Analysis:** Detects hyperfocus states and topic shifts. with YAML frontmatter containing behavioral states, physiological telemetry, and spatial coordinates.

---

## Installation Sequence (Windows ARM64 / PS7 Optimized)

1.  **Clone & Deploy:**
    ```powershell
    python deploy.py
    ```
    *This automatically creates the `vourdalak_env` sandbox, installs dependencies, and acquires the toolchain (Sherlock, Tor, etc.).*

2.  **Activate Sandbox:**
    ```powershell
    .\vourdalak_env\Scripts\activate
    ```

## Operational Interfaces

### GUI Mode (Human Control)
Launch the visual command center for point-and-click orchestration:
```powershell
python vourdalak_gui.py
```

### CLI Mode (Power User / AI)
Refer to `AGENT_PROTOCOL.md` for deterministic command schemas and autonomous workflows.

---

## Capabilities & Stealth
- **Portable Tor Circuit:** Automated IP obscuration via integrated Onion Routing.
- **Armory Vault:** Credential rotation and cooldown management for "Burner" accounts.
- **Multimodal Anchoring:** Synchronizes heart rate and location data with messaging events for deep behavioral profiling.

*Disclaimer: This tool is for authorized security research and digital twin construction only.*
