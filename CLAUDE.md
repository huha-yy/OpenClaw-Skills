# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **OpenClaw AI agent workspace** — not a traditional software project with build/test/lint infrastructure. There is no package.json, Makefile, or CI pipeline. The workspace is in its earliest stage: the git repo has no commits, and no application code has been written yet.

The project goal is to build a **Hotspot Monitoring & Social Media Content Operations Agent** (热点监控与自媒体内容运营方案) — an AI-agent-driven system that monitors online hot topics, determines relevance to a company/brand, performs multi-source fact-checking, generates platform-specific content (Xiaohongshu, Douyin, WeChat), and produces publishable content packages with risk reports.

**Primary language of planning documents:** Chinese (the operations team is Chinese-speaking, targeting Chinese social media platforms).

## Runtime

- **Framework:** OpenClaw / openclawd (Node.js-based AI agent orchestration platform)
- **LLM:** Xiaomi MiMo (miMo-v2-pro) via OpenClaw gateway
- **Gateway port:** 19000
- **Platform:** Windows 11 (China), but use Unix-style forward-slash paths
- **Installed via:** Scoop at `C:\Users\LENOVO1\scoop\apps\nodejs-lts\current\bin\openclaw.ps1`

## Repository Structure

```
D:\D-OpenClaw\
  .openclaw/              # OpenClaw runtime state (workspace-state.json)
  default/                # Parallel bootstrap copy of agent workspace (template/reference)
  docs/                   # System design documents (core workflow definition)
     openclaw_hotspot_media_workflow.md    # Main system design: 9-agent pipeline with module specs
     operations_requirements_template.md   # Requirements gathering template
     media_operation_workflow_plan_for_cto.md  # CTO-facing workflow summary
  logs/                   # OpenClaw gateway runtime logs
  运营Agent开发计划/       # "Operations Agent Development Plan" — phased implementation roadmap
     00_总计划.md          # Master plan with phase breakdown
     01_运营需求确认计划.md # Phase 0: Requirements confirmation
     02_本地POC开发计划.md  # Phase 1: Local POC development
     03_Agent工作流设计计划.md # Phase 2: Agent workflow design
     04_发布包与审核计划.md   # Phase 3: Publishing packages & review
     05_公司环境迁移计划.md   # Phase 4: Company environment migration
     06_自动化运营发布计划.md # Phase 4: Automated publishing
     07_技术栈选型文档.md     # **KEY**: Technology stack decisions and rationale
     08_图片策略文档.md       # Image sourcing strategy
  AGENTS.md               # OpenClaw workspace instructions (memory, heartbeats, group chats, boundaries)
  BOOTSTRAP.md            # First-run bootstrap script (workspace just seeded, identity not yet configured)
  HEARTBEAT.md            # Heartbeat poll configuration (currently empty)
  IDENTITY.md             # Agent identity template (name, vibe, emoji — not yet filled in)
  SOUL.md                 # Agent personality guidelines (core values, boundaries)
  TOOLS.md                # Local tool-specific notes (cameras, SSH, TTS — empty)
  USER.md                 # User profile template (not yet filled in)
```

## Architecture (Planned — Not Yet Implemented)

The system design defines a **9-agent pipeline** orchestrated by OpenClaw:

```
Monitor Agent → Relevance Agent → Research Agent → Strategy Agent
  → XHS Content Agent / Douyin Content Agent / WeChat Content Agent
  → Compliance Agent → Package Agent
```

Core workflow: `Hotspot detection → Relevance scoring → Multi-source fact-checking → Content generation (3 platforms) → Risk review → Publish package output`

### Phase 1 (Current Focus — Local POC)
- OpenClaw as orchestration hub + local Python/Node.js utility scripts
- File-based configuration (YAML/JSON/Markdown)
- Output: structured publish packages to `outputs/` directory
- SQLite for task records
- **Explicitly NO:** n8n, Dify, Coze, LangChain, LangGraph (deferred to Phase 2+)

### Phase 2+ (Future)
- Platform connectors (WeChat API, Xiaohongshu, Douyin)
- PostgreSQL/MySQL for company environment
- LangGraph for complex publish state machines, n8n for visual orchestration (optional)
- Review UI, approval flows, multi-account isolation

## Key Technical Decisions (from `07_技术栈选型文档.md`)

- OpenClaw is the **sole orchestration hub** for Phase 1 — no competing workflow engines
- LangChain is reserved for RAG/document processing needs only, not as the main framework
- LangGraph is only for Phase 2+ complex stateful publish workflows
- Image strategy: Pexels/stock photo search first, AI generation (Stable Diffusion/ComfyUI) as supplement
- Publishing is **human-reviewed** in Phase 1; auto-publish only for low-risk content in later phases

## Design Principles

- **Risk-aware:** Never auto-publish high-risk content (negative news, competitor criticism, policy disputes, financial/medical/legal topics). Always require human review for these.
- **Multi-source verification:** Never generate factual content from a single source. Cross-validate 2-3+ sources.
- **No platform scraping:** Only use official APIs, RSS, and publicly legal data sources. No client simulation or anti-bot bypassing.
- **Content transformation, not copying:** Re-create content based on facts, don't copy-paste original articles.

## Workspace Conventions

- The `AGENTS.md` file governs agent behavior (memory management, heartbeats, group chat conduct, external vs internal actions). Future Claude instances working here should follow those conventions.
- OpenClaw workspace files (`IDENTITY.md`, `USER.md`, `SOUL.md`, `TOOLS.md`, `HEARTBEAT.md`) are part of the agent's persistent identity — treat them as living configuration, not one-time templates.
- `BOOTSTRAP.md` indicates the workspace is un-configured. The first substantive conversation should establish the agent's identity and user profile, then delete `BOOTSTRAP.md`.
- The `default/` directory is a reference template — don't modify it without explicit intent.
