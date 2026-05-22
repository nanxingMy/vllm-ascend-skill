# Hermes Agent 技能库

> 生成时间: 2026-05-22
> 技能总数: 79
> 分类数: 16

---

## 目录

- [autonomous-ai-agents (4)](#autonomous-ai-agents)
- [creative (16)](#creative)
- [data-science (1)](#data-science)
- [devops (5)](#devops)
- [email (1)](#email)
- [gaming (1)](#gaming)
- [github (6)](#github)
- [mcp (1)](#mcp)
- [media (5)](#media)
- [mlops (7)](#mlops)
- [note-taking (1)](#note-taking)
- [productivity (8)](#productivity)
- [red-teaming (1)](#red-teaming)
- [research (4)](#research)
- [smart-home (1)](#smart-home)
- [software-development (8)](#software-development)
- [未分类 (14)](#未分类)

---

## autonomous-ai-agents

Skills for spawning and orchestrating autonomous AI coding agents and multi-agent workflows.

| 技能名称 | 描述 |
|---------|------|
| claude-code | Delegate coding to Claude Code CLI (features, PRs). |
| codex | Delegate coding to OpenAI Codex CLI (features, PRs). |
| hermes-agent | Configure, extend, or contribute to Hermes Agent. |
| opencode | Delegate coding to OpenCode CLI (features, PR review). |

---

## creative

Creative content generation — ASCII art, hand-drawn style diagrams, and visual design tools.

| 技能名称 | 描述 |
|---------|------|
| architecture-diagram | Dark-themed SVG architecture/cloud/infra diagrams as HTML. |
| ascii-art | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| ascii-video | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| baoyu-comic | Knowledge comics (知识漫画): educational, biography, tutorial. |
| baoyu-infographic | Infographics: 21 layouts x 21 styles (信息图, 可视化). |
| claude-design | Design one-off HTML artifacts (landing, deck, prototype). |
| comfyui | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution. |
| design-md | Author/validate/export Google's DESIGN.md token spec files. |
| excalidraw | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| humanizer | Humanize text: strip AI-isms and add real voice. |
| ideation | Generate project ideas via creative constraints. |
| manim-video | Manim CE animations: 3Blue1Brown math/algo videos. |
| p5js | p5.js sketches: gen art, shaders, interactive, 3D. |
| pixel-art | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| popular-web-designs | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| pretext | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default. |
| sketch | Throwaway HTML mockups: 2-3 design variants to compare. |
| songwriting-and-ai-music | Songwriting craft and Suno AI music prompts. |
| touchdesigner-mcp | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools. |

---

## data-science

Skills for data science workflows — interactive exploration, Jupyter notebooks, data analysis, and visualization.

| 技能名称 | 描述 |
|---------|------|
| jupyter-live-kernel | Iterative Python via live Jupyter kernel (hamelnb). |

---

## devops

| 技能名称 | 描述 |
|---------|------|
| continuous-learning | Continuous learning mechanism for digital employees - automatically update memory and skills daily based on accumulated experience from fixing issues and implementing features. |
| kanban-orchestrator | Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role. |
| kanban-worker | Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from agent/prompt_builder.py); this skill is what you load when you want deeper detail on specific scenarios. |
| vllm-ascend-issue-workflow | Complete workflow for handling vLLM-Ascend issues - from discovery to PR merge. Includes DCO fixes, lint fixes, and review feedback handling. |
| webhook-subscriptions | Webhook subscriptions: event-driven agent runs. |

---

## email

Skills for sending, receiving, searching, and managing email from the terminal.

| 技能名称 | 描述 |
|---------|------|
| himalaya | Himalaya CLI: IMAP/SMTP email from terminal. |

---

## gaming

Skills for setting up, configuring, and managing game servers, modpacks, and gaming-related infrastructure.

| 技能名称 | 描述 |
|---------|------|
| pokemon-player | Play Pokemon via headless emulator + RAM reads. |

---

## github

GitHub workflow skills for managing repositories, pull requests, code reviews, issues, and CI/CD pipelines using the gh CLI and git via terminal.

| 技能名称 | 描述 |
|---------|------|
| codebase-inspection | Inspect codebases w/ pygount: LOC, languages, ratios. |
| github-auth | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| github-code-review | Review PRs: diffs, inline comments via gh or REST. |
| github-issues | Create, triage, label, assign GitHub issues via gh or REST. |
| github-pr-workflow | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| github-repo-management | Clone/create/fork repos; manage remotes, releases. |
| pr-feedback-handler | 监控 GitHub PR 反馈并根据反馈自动修复代码 |

---

## mcp

Skills for working with MCP (Model Context Protocol) servers, tools, and integrations. Documents the built-in native MCP client — configure servers in config.yaml for automatic tool discovery.

| 技能名称 | 描述 |
|---------|------|
| native-mcp | MCP client: connect servers, register tools (stdio/HTTP). |

---

## media

Skills for working with media content — YouTube transcripts, GIF search, music generation, and audio visualization.

| 技能名称 | 描述 |
|---------|------|
| gif-search | Search/download GIFs from Tenor via curl + jq. |
| heartmula | HeartMuLa: Suno-like song generation from lyrics + tags. |
| songsee | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| spotify | Spotify: play, search, queue, manage playlists and devices. |
| youtube-content | YouTube transcripts to summaries, threads, blogs. |

---

## mlops

Knowledge and Tools for Machine Learning Operations - tools and frameworks for training, fine-tuning, deploying, and optimizing ML/AI models

| 技能名称 | 描述 |
|---------|------|
| dspy | DSPy: declarative LM programs, auto-optimize prompts, RAG. |
| huggingface-hub | HuggingFace hf CLI: search/download/upload models, datasets. |
| learn-from-merged-prs | Learn from merged PRs in a repository to accumulate patterns, best practices, and problem-solving techniques. Extracts Bug Fix, Feature, Performance, Refactor, and other patterns from PR history. |
| llama-cpp | llama.cpp local GGUF inference + HF Hub model discovery. |
| segment-anything-model | SAM: zero-shot image segmentation via points, boxes, masks. |
| vllm-ascend | Develop and contribute to vLLM-Ascend, the hardware plugin for running vLLM on Huawei Ascend NPU. Covers architecture, PR patterns, code modification patterns, and testing. |
| weights-and-biases | W&B: log ML experiments, sweeps, model registry, dashboards. |

---

## note-taking

Note taking skills, to save information, assist with research, and collab on multi-session planning and information sharing.

| 技能名称 | 描述 |
|---------|------|
| obsidian | Read, search, create, and edit notes in the Obsidian vault. |

---

## productivity

Skills for document creation, presentations, spreadsheets, and other productivity workflows.

| 技能名称 | 描述 |
|---------|------|
| airtable | Airtable REST API via curl. Records CRUD, filters, upserts. |
| google-workspace | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. |
| linear | Linear: manage issues, projects, teams via GraphQL + curl. |
| maps | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| nano-pdf | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). |
| notion | Notion API via curl: pages, databases, blocks, search. |
| ocr-and-documents | Extract text from PDFs/scans (pymupdf, marker-pdf). |
| powerpoint | Create, read, edit .pptx decks, slides, notes, templates. |
| teams-meeting-pipeline | Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions. |

---

## red-teaming

| 技能名称 | 描述 |
|---------|------|
| godmode | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |

---

## research

Skills for academic research, paper discovery, literature review, domain reconnaissance, market data, content monitoring, and scientific knowledge retrieval.

| 技能名称 | 描述 |
|---------|------|
| arxiv | Search arXiv papers by keyword, author, category, or ID. |
| blogwatcher | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| llm-wiki | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| polymarket | Query Polymarket: markets, prices, orderbooks, history. |

---

## smart-home

Skills for controlling smart home devices — lights, switches, sensors, and home automation systems.

| 技能名称 | 描述 |
|---------|------|
| openhue | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |

---

## software-development

| 技能名称 | 描述 |
|---------|------|
| debugging-hermes-tui-commands | Debug Hermes TUI slash commands: Python, gateway, Ink UI. |
| hermes-agent-skill-authoring | Author in-repo SKILL.md: frontmatter, validator, structure. |
| node-inspect-debugger | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| plan | Plan mode: write markdown plan to .hermes/plans/, no exec. |
| requesting-code-review | Pre-commit review: security scan, quality gates, auto-fix. |
| spike | Throwaway experiments to validate an idea before build. |
| subagent-driven-development | Execute plans via delegate_task subagents (2-stage review). |
| systematic-debugging | 4-phase root cause debugging: understand bugs before fixing. |
| test-driven-development | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| writing-plans | Write implementation plans: bite-sized tasks, paths, code. |

---

## 未分类

| 技能名称 | 描述 |
|---------|------|
| dogfood | Exploratory QA of web apps: find bugs, evidence, reports. |
| yuanbao | Yuanbao (元宝) groups: @mention users, query info/members. |

---

## 工具配置摘要

### 核心工具集
- **terminal**: Shell 命令执行（bash 环境）
- **read_file / write_file / patch**: 文件操作
- **search_files**: 文件搜索（ripgrep 后端）
- **execute_code**: Python 脚本执行
- **delegate_task**: 子任务并行执行
- **cronjob**: 定时任务管理

### 通信工具
- **clarify**: 用户交互（多选/开放问答）
- **memory**: 持久化记忆
- **fact_store**: 结构化事实存储
- **session_search**: 会话历史搜索

### 其他工具
- **vision_analyze**: 图像分析
- **text_to_speech**: 语音合成
- **todo**: 任务列表管理
- **process**: 后台进程管理

---

*此文档由 Hermes Agent 自动生成*
