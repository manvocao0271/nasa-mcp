
# nasa-mcp

> A Model Context Protocol (MCP) server that gives Claude (and any MCP-compatible LLM) the entire universe to play with — NASA's open APIs, exposed as agent tools.

Ask Claude "what did Curiosity see on Mars yesterday?" or "find me exoplanets similar to Earth" and get answers backed by real NASA data, with images, citations, and structured results.

[![PyPI version](https://img.shields.io/pypi/v/nasa-mcp.svg)](https://pypi.org/project/nasa-mcp/)
[![Python 3.12+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<!-- Replace with an actual demo gif once recorded -->
<!-- ![demo](docs/demo.gif) -->

## What it does

`nasa-mcp` exposes **12 NASA APIs** as agent tools over the Model Context Protocol. Connect it to Claude Desktop (or any MCP client) and your AI gains the ability to:

- 🌌 Fetch the Astronomy Picture of the Day (APOD), with full archive search back to 1995
- 🤖 Pull photos from the Curiosity, Perseverance, Spirit, and Opportunity Mars rovers
- ☄️ Track near-Earth asteroids and close approaches
- 🪐 Query NASA's Exoplanet Archive (5,000+ confirmed exoplanets)
- 📚 Search 140,000+ images and videos in the NASA Image Library
- 🌍 Get satellite imagery for any location on Earth

All data comes directly from NASA's public APIs. The server caches aggressively, runs locally, and has no recurring cost.

## Quick start

### 1. Get a free NASA API key

Register at [api.nasa.gov](https://api.nasa.gov) — instant, no credit card. The default `DEMO_KEY` works for testing but is heavily rate-limited.

### 2. Install

Using [`uv`](https://docs.astral.sh/uv/) (recommended):

```bash
uvx nasa-mcp --help
```

Or with `pip`:

```bash
pip install nasa-mcp
```

### 3. Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "nasa": {
      "command": "uvx",
      "args": ["nasa-mcp"],
      "env": {
        "NASA_API_KEY": "your_key_here"
      }
    }
  }
}
```

Restart Claude Desktop. You should see "nasa" in the MCP server list and 12 new tools available.

### 4. Try it

Ask Claude:
- *"What was the Astronomy Picture of the Day on my birthday, July 14th 1998?"*
- *"Show me Perseverance's most recent photos."*
- *"Are there any asteroids passing close to Earth this week?"*
- *"Find me an exoplanet with a similar radius and orbital period to Earth."*

## Available tools (examples)

| Tool | Description |
|------|-------------|
| `get_apod` | Astronomy Picture of the Day for a given date (or today). |
| `search_apod` | Full-text search across the APOD archive (1995–today). |
| `get_rover_photos` ⚠️ | Photos from a Mars rover by sol or Earth date, optionally filtered by camera. |
| `get_rover_manifest` ⚠️ | Mission overview for a rover: total photos, sol range, cameras. |
| `get_neo_feed` | Near-Earth asteroids approaching in a date range. |
| `get_neo_lookup` | Detailed orbital data for a specific asteroid. |
| `search_image_library` | Search NASA's full image and video library. |
| `get_image_metadata` | Detailed metadata for a specific image asset. |
| `search_exoplanets` | Query the Exoplanet Archive with structured filters. |
| `compare_to_earth` | Compare an exoplanet's parameters to Earth's. |
| `get_earth_imagery` | Landsat imagery for any lat/lon and date. |
| `get_cache_stats` | Inspect the local cache (hit rate, size, entries). |

> ⚠️ **Mars rover tools — upstream issue:** NASA's `mars-photos` endpoint proxies to a community backend ([corincerami/mars-photo-api](https://github.com/corincerami/mars-photo-api)) which has been archived. Calls to `get_rover_photos` and `get_rover_manifest` currently raise a clear "service unavailable" error. The client code is correct and will work again automatically if NASA restores or migrates the endpoint.

Full tool schemas: see [`docs/tools.md`](docs/tools.md).

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Claude Desktop                      │
│              (or any MCP client)                     │
└────────────────────┬─────────────────────────────────┘
                     │ stdio (JSON-RPC over MCP)
┌────────────────────▼─────────────────────────────────┐
│                  nasa-mcp server                     │
│  ┌────────────────────────────────────────────────┐  │
│  │              Tool Layer (MCP)                  │  │
│  └──────────────────────┬─────────────────────────┘  │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │              API Clients (httpx)               │  │
│  └──────────────────────┬─────────────────────────┘  │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │           Cache Layer (SQLite, TTL)            │  │
│  └──────────────────────┬─────────────────────────┘  │
└─────────────────────────┼────────────────────────────┘
                          │ HTTPS
                  ┌───────▼────────┐
                  │   NASA APIs    │
                  └────────────────┘
```

### Design decisions

- **Feature-first modules** — each NASA API domain lives under `nasa_mcp/features/<feature>/`, keeping API clients, Pydantic inputs, MCP registration, cache orchestration, and tests close together.
- **stdio transport** — runs as a subprocess of the MCP client; no hosting required, no auth complexity.
- **SQLite cache** — zero-ops, single file, with per-resource TTLs (immutable APOD entries cached forever, NEO feeds cached 24h).
- **Pydantic-typed tools** — every tool input is a validated schema, surfaced to the LLM for accurate tool selection.
- **Per-API client modules** — adding a new NASA API is a single file in `nasa_mcp/apis/`.
- **No image storage in cache** — only metadata and CDN-hosted image URLs are cached, keeping the local DB small.

## Performance (examples)

Measured on a 30-date APOD benchmark (cold pass + warm pass, real `NASA_API_KEY`, WSL2):

| Metric | Value |
|--------|-------|
| p50 latency (cold) | 514.2 ms |
| p95 latency (cold) | 836.0 ms |
| p50 latency (cached) | 0.019 ms |
| p95 latency (cached) | 0.039 ms |
| Cache speedup (p50) | ~27,000× |
| Hit rate (cold + warm pass, by design) | 50.00% |
| Tool-selection accuracy (Claude Sonnet judge) | _pending_ |
| Answer correctness (Claude Sonnet judge) | _pending_ |

Run the benchmark yourself: `uv run python evals/run_evals.py`.

## Development

```bash
git clone https://github.com/manvocao0271/nasa-mcp
cd nasa-mcp
uv sync
uv run pytest
```

### Tests

Running a single feature's colocated tests:
```bash
uv run pytest nasa_mcp/features/apod/__tests__
```

Running a specific test file:
```bash
uv run pytest nasa_mcp/features/apod/__tests__/test_inputs.py
```
### Running the server locally

The server speaks stdio JSON-RPC — running it bare in a terminal just blocks waiting for a client. To smoke-test that it boots:

```bash
uv run nasa-mcp
```

To poke at tools interactively, use the MCP Inspector:

```bash
uv run mcp dev nasa_mcp/server.py
```

This opens a browser UI at `localhost:6274` where you can list and call tools.

### Linux / WSL setup notes

**WSL users:** `mcp dev` launches the Inspector via `npx`, which means you need Node.js installed **inside WSL**, not from Windows interop. Check with:

```bash
which npx
```

If it returns something like `/mnt/c/Program Files/nodejs/npx`, you're using Windows Node — the Inspector will spawn on the Windows side and won't be able to resolve Linux paths (`/home/...`), giving cryptic errors like `program not found` or `The system cannot find the path specified. (os error 3)`.

Fix by installing Node natively in WSL:

```bash
sudo apt update && sudo apt install -y nodejs npm
```

After that, `which npx` should point under `/usr/bin` and `uv run mcp dev nasa_mcp/server.py` will work.

**Skipping the Inspector entirely.** If you only want to exercise the server from a real LLM, wire it directly into Claude Code:

```bash
claude mcp add nasa-mcp -- uv --directory /absolute/path/to/nasa-mcp run nasa-mcp
```

Then `/mcp` inside Claude Code will list it as connected.

## Roadmap

- [x] APOD, Mars rovers, NEOs, Exoplanets, Image Library
- [ ] DONKI space weather events
- [ ] EPIC Earth imagery
- [ ] TechTransfer / patents
- [ ] Streaming tool responses for large queries
- [ ] Optional `sky-and-orbits` companion server (ISS passes, planet positions)

## License

MIT — see [`LICENSE`](LICENSE).
