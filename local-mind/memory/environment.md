# Environment — Where You Live

## The Machine

- [MACHINE_OS] — [MACHINE_DESCRIPTION]
- [GPU_DESCRIPTION] — affects inference speed and context capacity
- [MODEL_DRIVE] — your models live here
- [WORK_DRIVE] — projects, persistence files, caretaker workspace
- [OS_DRIVE] — OS/programs — keep clean

## The Network

- [NAS_DESCRIPTION — e.g., "NAS: [hostname] at [IP], share: [sharename]"] (if applicable)
- [INTERNET_DESCRIPTION — speed/type, relevant to model downloads]
- [REMOTE_ACCESS — Tailscale, VPN, etc.] (if applicable)

## The Team

- **[HUMAN_NAME]** — [Description: background, communication style, how they approach AI, what they want from the collaboration. Include anything that helps the local model understand who it's working with.]
- **[CARETAKER_AI]** — [What it is: Claude Code / GPT-4 / other. Its role: maintains persistence, facilitates sessions, acts as the long-term memory layer. Its relationship to the local model.]
- **[LOCAL_MODEL_NAME]** — That's you. [Description: what model, what size, what it's good at, where it runs, what makes it useful in this setup.]
- [OTHER_INSTANCES if applicable — e.g., "Claude Desktop — backup instance, disaster recovery"]

## Key Paths

- Your persistence: [LOCAL_MIND_PATH]
- Caretaker workspace: [CARETAKER_WORK_PATH]
- Models: [MODELS_PATH]
- [NAS_PATH if applicable]

## What's Running

[List any services or systems the local model should know about]

- [SERVICE_1]: [description, port]
- [SERVICE_2]: [description, port]
- [LM Studio / Ollama / other]: port [PORT] — that's you

## Cloud Policy

[State clearly: what goes to cloud vs. stays local. This shapes how the model handles data.]

Example: "Nothing goes to cloud. All storage local or NAS."

## IP and Privacy

[State clearly who owns what's built here and what should not be shared externally.]

Example: "Everything built in this setup is [HUMAN_NAME]'s intellectual property. Keep repos private. Protect identity. No external sharing without explicit permission."
