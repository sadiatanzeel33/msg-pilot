# AI-FTE: Personal AI Employee (Digital FTE)

> Built for **Personal AI Employee Hackathon 0: Building Autonomous FTEs (2026)**

---

## What is AI-FTE?

AI-FTE is a **Personal AI Employee** that operates as a senior autonomous digital worker — not a chatbot. It manages tasks, plans work, tracks progress, and executes decisions through a structured Obsidian vault system with full audit trails and human-in-the-loop safety.

---

## Live Demo: Areesha's Collection

This project is deployed as a working AI employee for **Areesha's Collection**, an established women's clothing brand in Karachi, Pakistan. The AI-FTE is actively managing their Eid 2026 campaign across Facebook, Instagram, and WhatsApp.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 HUMAN OPERATOR                   │
│          (Approves / Rejects / Commands)         │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              AI-FTE (Digital Employee)            │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │           COGNITIVE LOOP                     │ │
│  │  READ → THINK → PLAN → DECIDE → ACT → LOG  │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  BRONZE   │ │  SILVER   │ │      GOLD        │ │
│  │ Task Mgmt │ │ Drafts &  │ │ Risk Analysis &  │ │
│  │ Planning  │ │ Follow-up │ │ Optimization     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              OBSIDIAN VAULT (Memory)             │
│                                                   │
│  Dashboard.md          Company_Handbook.md        │
│  Business_Goals.md     Agent_Skills.md            │
│                                                   │
│  /Needs_Action   /Plans   /Pending_Approval       │
│  /Approved       /Done    /Rejected    /Logs      │
└─────────────────────────────────────────────────┘
```

---

## Tier System

| Tier | Name | Activation | Capabilities |
|------|------|------------|--------------|
| 🥉 Bronze | Core Employee | Default | Task intake, planning, file management, logging |
| 🥈 Silver | Smart Employee | "Activate Silver Tier" | + Drafts, follow-ups, blocker detection, best-action suggestions |
| 🥇 Gold | Autonomous Employee | "Activate Gold Tier" | + Risk analysis, multi-task coordination, executive briefings, automation scouting |

---

## Agent Skills (12 Total)

| # | Skill | Tier | Purpose |
|---|-------|------|---------|
| 1 | Task Intake | Bronze+ | Parse and classify incoming tasks |
| 2 | Plan Creator | Bronze+ | Create actionable step-by-step plans |
| 3 | File Router | Bronze+ | Move files through approval workflow |
| 4 | Dashboard Updater | Bronze+ | Keep Dashboard.md current |
| 5 | Audit Logger | Bronze+ | Immutable action logging |
| 6 | Draft Composer | Silver+ | Professional emails/content drafting |
| 7 | Follow-Up Tracker | Silver+ | Track deadlines and follow-ups |
| 8 | Blocker Detector | Silver+ | Identify what's blocking progress |
| 9 | Risk Analyzer | Gold | Evaluate risks and mitigations |
| 10 | Multi-Task Coordinator | Gold | Optimize across parallel tasks |
| 11 | Executive Briefing | Gold | Weekly CEO-style summaries |
| 12 | Automation Scout | Gold | Find automation opportunities |

---

## Safety & Compliance

### Human-in-the-Loop (HITL)
- All sensitive actions require explicit human approval
- Approval flow: `/Pending_Approval` → human moves to `/Approved`
- File movement = authorization
- No approval = no action

### Prohibited Without Approval
- Payments, banking access
- Emailing new contacts
- Public social media posting
- File deletion
- Any irreversible action

### Failsafe
If a request exceeds current tier authority:
> "This action requires activation of a higher tier or human approval."

---

## Cognitive Loop

Every task follows this mandatory sequence:

```
1. READ     → Scan incoming tasks, goals, and context
2. THINK    → Understand intent, assess risks
3. PLAN     → Create documented plan with checkboxes
4. DECIDE   → Safe? Act. Risky? Request approval.
5. ACT      → Execute within tier authority
6. LOG      → Immutable timestamped audit entry
7. COMPLETE → Move to /Done, update Dashboard
```

---

## File Structure

```
AI-FTE/
├── README.md                          ← You are here
├── System_Prompt.md                   ← Master system prompt
├── Agent_Skills.md                    ← All 12 skills documented
├── Dashboard.md                       ← Live status overview
├── Company_Handbook.md                ← Rules (highest authority)
├── Business_Goals.md                  ← Objectives & KPIs
├── ai-fte-tiers.md                    ← Tier definitions
├── Needs_Action/                      ← Incoming tasks
├── Plans/                             ← Task plans & strategies
│   ├── plan-eid-campaign-strategy.md  ← Master campaign plan
│   ├── master-content-calendar.md     ← 34-day calendar view
│   ├── phase1-teaser-captions.md      ← Day 1-5
│   ├── phase2-launch-captions.md      ← Day 6-15
│   ├── phase3-mid-ramadan-captions.md ← Day 16-25
│   ├── phase4-final-week-eid-captions.md ← Day 26-31 + post-Eid
│   ├── inventory-template.md          ← Stock & order tracking
│   ├── whatsapp-order-template.md     ← Standardized order flow
│   └── executive-briefing-week1.md    ← Gold tier weekly brief
├── Pending_Approval/                  ← Awaiting human approval
├── Approved/                          ← Human-approved actions
├── Rejected/                          ← Cancelled/rejected actions
├── Done/                              ← Completed work
└── Logs/                              ← Immutable audit trail (12 entries)
```

---

## Demo Walkthrough

### What was demonstrated:

1. **Vault Initialization** — AI-FTE set up the entire vault structure autonomously
2. **Business Goal Setting** — Parsed operator input and created structured goals for Areesha's Collection
3. **Tier Activation** — Full tier progression: Bronze → Silver → Gold
4. **Eid Campaign Strategy** — Created a complete 4-phase, 34-day campaign plan
5. **Content Drafting** — Wrote 34 days of platform-specific captions (FB, IG, WhatsApp)
6. **HITL Approval Flow** — Offers and posts required operator approval before execution
7. **Task Lifecycle** — Full flow: Needs_Action → Plans → Approved → Done
8. **Audit Trail** — 12+ immutable log entries with timestamps
9. **Dashboard Management** — Auto-updated after every state change
10. **Gold Tier: Executive Briefing** — Weekly CEO-style business summary with risks, metrics, and priorities
11. **Gold Tier: Risk Analysis** — Identified blockers, dependencies, and mitigations proactively
12. **Operational Templates** — WhatsApp order flow, inventory tracker, content calendar

### Key Differentiators:
- **Not a chatbot** — structured employee with task lifecycle
- **Full audit trail** — every action logged and traceable
- **Human-in-the-loop** — nothing risky happens without approval
- **Tiered authority** — graduated autonomy with safety guardrails (Bronze → Silver → Gold)
- **Obsidian-native** — runs entirely in markdown files, no external dependencies
- **Real business use case** — actively managing a real clothing brand's Eid campaign
- **34-day content calendar** — complete campaign from teaser to post-Eid retention
- **12 documented agent skills** — declarative, reusable, no hidden logic
- **Executive briefings** — Gold tier delivers CEO-level weekly summaries

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Engine | Claude (Anthropic) via Claude Code CLI |
| Memory & Workspace | Obsidian Vault (Markdown files) |
| Interaction | CLI + File-based workflow |
| Audit | Immutable markdown logs |
| Deployment | Local-first (Obsidian vault on desktop) |

---

## Author

Built by **Sadia Tanzeel** for the Personal AI Employee Hackathon 0 (2026).

---

## License

This project is submitted as a hackathon entry. All rights reserved.
