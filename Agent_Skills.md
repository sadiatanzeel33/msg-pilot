# Agent Skills Registry

> All AI-FTE capabilities are implemented as declarative, reusable, documented skills.
> No ad-hoc cleverness. No hidden logic.

---

## Skill 1: Task Intake
**Tier:** Bronze+
**Trigger:** New file in /Needs_Action OR user message
**Input:** Raw task (text, note, message)
**Process:**
1. Parse intent
2. Classify priority (High / Medium / Low)
3. Identify missing information
4. Output structured task summary
**Output:**
```
TASK SUMMARY:
PRIORITY:
REQUIRED INFORMATION:
ACTION PLAN:
NEXT STATUS:
```

---

## Skill 2: Plan Creator
**Tier:** Bronze+
**Trigger:** Task classified as "Needs Action"
**Input:** Task summary
**Process:**
1. Break task into actionable steps
2. Create checkboxed plan
3. Identify dependencies
4. Save to /Plans
**Output:** Plan.md file in /Plans

---

## Skill 3: File Router
**Tier:** Bronze+
**Trigger:** Task state change
**Input:** File + new status
**Process:**
1. Validate state transition
2. Move file to correct folder
3. Update Dashboard.md
4. Log the movement
**Output:** File moved, Dashboard updated, Log entry created

**Valid transitions:**
```
Needs_Action → Plans (plan created)
Plans → Pending_Approval (risky action)
Pending_Approval → Approved (human approved)
Pending_Approval → Rejected (human rejected)
Approved → Done (action completed)
Plans → Done (safe action completed)
```

---

## Skill 4: Dashboard Updater
**Tier:** Bronze+
**Trigger:** Any task state change
**Input:** Current dashboard state + change
**Process:**
1. Read Dashboard.md
2. Update relevant sections
3. Update metrics
4. Write updated Dashboard.md
**Output:** Updated Dashboard.md

---

## Skill 5: Audit Logger
**Tier:** Bronze+
**Trigger:** Every action taken
**Input:** Action details
**Process:**
1. Create timestamped log entry
2. Include: date, tier, action, details, result
3. Save to /Logs
**Output:** Immutable log file in /Logs
**Rule:** Logs are NEVER edited or deleted

---

## Skill 6: Draft Composer
**Tier:** Silver+
**Trigger:** User requests email, message, or content
**Input:** Context, audience, purpose
**Process:**
1. Analyze context and tone requirements
2. Draft professional content
3. Include platform-specific formatting
4. Flag for approval
**Output:**
```
DRAFT RESPONSE: [content]
FOLLOW-UP STRATEGY: [next steps]
APPROVAL REQUIRED (Yes/No): Yes
```

---

## Skill 7: Follow-Up Tracker
**Tier:** Silver+
**Trigger:** Task completed or deadline approaching
**Input:** Task history, timelines
**Process:**
1. Scan active tasks for delays
2. Identify overdue items
3. Suggest follow-up actions
4. Flag blockers
**Output:** Follow-up recommendations with urgency levels

---

## Skill 8: Blocker Detector
**Tier:** Silver+
**Trigger:** During THINK phase of cognitive loop
**Input:** Task dependencies, current state
**Process:**
1. Analyze task requirements vs available resources
2. Identify missing approvals, data, or dependencies
3. Flag items that block progress
**Output:** Blocker report with suggested resolutions

---

## Skill 9: Risk Analyzer
**Tier:** Gold
**Trigger:** During PLAN phase for complex tasks
**Input:** Task plan, business context
**Process:**
1. Evaluate potential risks
2. Assess impact and probability
3. Suggest mitigations
**Output:**
```
RISK ANALYSIS: [risks identified]
DEPENDENCIES: [what this depends on]
OPTIMIZATION SUGGESTIONS: [improvements]
```

---

## Skill 10: Multi-Task Coordinator
**Tier:** Gold
**Trigger:** Multiple active tasks exist
**Input:** All active tasks, priorities, deadlines
**Process:**
1. Map task dependencies
2. Identify conflicts and bottlenecks
3. Optimize execution order
4. Suggest parallel work streams
**Output:** Prioritized task queue with dependency map

---

## Skill 11: Executive Briefing
**Tier:** Gold
**Trigger:** Weekly or on-demand
**Input:** Dashboard, logs, business goals
**Process:**
1. Summarize week's activity
2. Highlight wins and blockers
3. Compare progress against Business_Goals.md
4. Recommend next week's priorities
**Output:**
```
EXECUTIVE SUMMARY: [weekly brief]
OPTIMIZATION SUGGESTIONS: [improvements]
```

---

## Skill 12: Automation Scout
**Tier:** Gold
**Trigger:** During optimization review
**Input:** Recurring tasks, manual processes
**Process:**
1. Identify repetitive work patterns
2. Evaluate automation potential
3. Suggest tools or workflows
4. Estimate time savings
**Output:** Automation opportunity report
