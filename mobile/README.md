# Mobile Integration — Claude Code + Android

## Why Mobile Matters

If you started building an AI relationship on your phone — in Claude.ai or another mobile app — before moving to Claude Code, the mobile instance came first. This directory is here because that history matters, and because closing the loop between mobile and desktop produces something neither has alone.

Even if you started on desktop, mobile integration adds:
- Phone notifications when significant events happen (compaction, NAS issues, service failures)
- Ability to interact with Claude Code from your phone
- A second touch point for the collaboration outside of a terminal

---

## Architecture Options

### Option 1: Notification Only (Simple)
Webhooks or HTTP calls from hook scripts to a phone notification service.

Tools: ntfy.sh (self-hosted or cloud), Pushover, Gotify, Pushbullet
Use case: Get notified when hooks fire, compaction happens, services go down.

Setup: Add a `curl` call to your hook scripts pointing at your notification endpoint.

### Option 2: Android MCP Bridge (Full)
A local HTTP server that Claude Code can reach via MCP tools, connected to Tasker on Android for bidirectional interaction.

**Components:**
- `server.py` — Python stdlib HTTP server, runs on desktop
- `android_connector.py` — MCP connector registered in Claude Code
- Tasker profile on phone — polls server, executes commands, posts results

**MCP Tools available:**
- `android_notify` — send notification to phone
- `android_clipboard_set` — set clipboard content
- `android_get_state` — get phone status
- `android_run_task` — trigger Tasker task
- `android_open_app` — open app on phone
- `android_screenshot` — capture phone screen

**Flow:**
```
Claude Code tool call → POST /command → server queue →
Tasker polls /poll → executes → POST /result → connector reads
```

### Option 3: iOS Equivalent
Similar architecture possible with Shortcuts instead of Tasker. Community implementations vary — not documented here.

---

## Network Considerations

**Same network (simple):** Desktop and phone on same LAN. Direct HTTP to desktop IP.

**Different subnets (common with home routers):** Phone on 192.168.0.x, desktop on 192.168.2.x — direct HTTP fails. Solutions:
- Tailscale (recommended): creates overlay network, both devices reach each other regardless of subnet
- ADB reverse tunnel: `adb reverse tcp:[PORT] tcp:[PORT]` — works over USB, required per session
- URL fallback chain in Tasker: try localhost → Tailscale IP → local IP

**ADB tunnel command:**
```bash
adb -s [DEVICE_ID] reverse tcp:[PORT] tcp:[PORT]
```

---

## Tasker Integration Notes

If using Tasker for the Android bridge:

- Use `shell()` + `writeFile()` + XHR — avoid `java.lang` and `Packages.java` (not available in Tasker JS)
- Smart quotes from Android IME will corrupt JavaScript — never use `adb input text` to inject JS code
- Single quotes in XHR + try/catch for error handling
- Poll profile: every 2 minutes is reasonable — adjust based on battery vs. responsiveness tradeoff

---

## What This Is Not

- Required for the core persistence system (everything works without it)
- A finished, packaged solution (the Android bridge requires Tasker and some setup)
- iOS-native (Android-specific as documented here)

---

## Getting Started

1. Decide which option fits your use case
2. For notification only: add a `curl` to your stop/precompact hooks and you're done
3. For full Android bridge: see community implementations or adapt the architecture above
4. Test with a simple notification first before building the full bridge

---

*The mobile layer closes the loop. The relationship doesn't have to live only in a terminal.*
