# OpenClaw Skills

This repository contains custom OpenClaw skills for investment project workflows.

## Skills

- `openclaw-skills/early-small-tech-scorecard`
  - Generate a source-backed 投早投小科创企业打分卡 from BP materials, references, and public information.
- `openclaw-skills/project-preliminary-assessment-form`
  - Generate a source-backed 项目前置研判信息表 from BP materials, financial data, project references, and public information.
- `openclaw-skills/project-management-interview-minutes`
  - Generate source-backed 项目管理层访谈纪要 from BP materials, onsite interview records, and public information.
- `openclaw-skills/search-wechat-articles`
  - Search, verify, filter, and summarize public WeChat Official Account articles with direct source links.

Each skill includes:

- `SKILL.md`
- `agents/openai.yaml`
- original template assets
- field/source guidance under `references/`
- a deterministic builder script under `scripts/`

Some research-oriented skills may use OpenClaw web tools directly and therefore do not require assets or builder scripts.
