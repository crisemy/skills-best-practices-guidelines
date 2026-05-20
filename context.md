# Project Context: Agent Skills Design Best Practices & Validation Toolkit

## Project Overview

This repository is a professional-grade guide and automated validation toolkit for authoring **Agent Skills** that comply with the `agentskills.io` specification and optimal LLM discoverability guidelines. It provides both conceptual best practices and an automated enforcement mechanism to ensure skills are structured, validated, and deployable to agent platforms.

The original concept was created by [@mgechev](https://github.com/mgechev/), but this implementation has been completely refactored, fixed, and expanded into a fully operational validation suite with 100% alignment to [Anthropic / Claude's official Agent Skills guidelines](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

---

## Purpose & Goals

### Primary Goals
1. **Enforce Compliance**: Automatically validate that agent skills meet strict naming, description, and structural standards before deployment.
2. **Optimize Discoverability**: Ensure skill metadata (name and description) are structured for maximum LLM routing accuracy and context window efficiency.
3. **Enforce Progressive Disclosure**: Keep skill instructions lean (under 500 lines) by moving complex schemas and procedures to references and assets.
4. **Prevent Hallucination**: Eliminate ambiguity by enforcing deterministic steps, clear error handling, and explicit negative triggers.

### Key Improvements Over Original
- **Fixed Core Execution**: Original was non-functional; rebuilt from scratch as a fully operational suite.
- **Multiple Testing Interfaces**: Interactive TUI menu, file validation, batch folder scanning, and direct CLI mode.
- **12 Comprehensive Compliance Checks**: Expanded from basic checks to cover all aspects of Agent Skills best practices.
- **YAML Frontmatter Parser**: Automatically extracts and validates metadata directly from `SKILL.md` files.
- **Production-Ready**: Implements 100% of Anthropic's official guidelines.

---

## Project Structure

```
skills-best-practices/
├── README.md                      # Full documentation and validator guide
├── linkedin-speach.md             # LinkedIn article summarizing the project
├── context.md                     # This file - project context and architecture
└── skill/
    ├── SKILL.md                   # Skill authoring procedure (agentskills.io spec)
    ├── assets/
    │   └── SKILL.template.md      # Base template for creating new skills
    ├── references/
    │   └── checklist.md           # Final validation checklist before deployment
    └── scripts/
        └── validate-metadata.py   # Core validation engine (12 compliance checks)
```

---

## Core Components

### 1. **validate-metadata.py** - The Validation Engine
The heart of the toolkit. A robust Python script that enforces 12 separate compliance checks:

#### Execution Modes
- **Interactive TUI Mode** (no args): Launches a retro terminal dashboard for quick testing
  ```bash
  python skill/scripts/validate-metadata.py
  ```

- **File Validation Mode**: Extracts metadata from YAML frontmatter and validates SKILL.md
  ```bash
  python skill/scripts/validate-metadata.py --skillToValidate path/to/SKILL.md
  ```

- **Batch Folder Mode**: Scans entire skill directories and generates compliance reports
  ```bash
  python skill/scripts/validate-metadata.py --skillFolder path/to/skills/
  ```

- **Direct CLI Mode**: Validates skill name and description as command-line arguments
  ```bash
  python skill/scripts/validate-metadata.py --name "my-skill" --description "Enables X. Use when Y..."
  ```

### 2. **SKILL.md** - The Authoring Guide
A procedural skill that walks users through the 5-step process to create compliant agent skills:
1. Initialize and validate metadata
2. Structure the directory
3. Draft core logic with progressive disclosure
4. Identify and bundle scripts
5. Perform final validation

### 3. **assets/SKILL.template.md** - Boilerplate
Starter template with the required YAML frontmatter structure and example procedure sections.

### 4. **references/checklist.md** - Pre-Deployment Audit
Final manual checklist covering 5 categories:
- Metadata & discovery (naming, triggers, tone)
- File structure & paths
- Logic & instructions
- Scripts & determinism
- Error handling

---

## The 12 Automated Compliance Checks

The validator enforces the following rules:

| # | Check | Field | Severity | Rule |
|---|-------|-------|----------|------|
| 1 | **Name Length** | `name` | Error | Must be 1–64 characters |
| 2 | **Character Rules** | `name` | Error | Lowercase, numbers, single hyphens only; no leading/trailing hyphens |
| 3 | **No XML Tags** | `name` | Error | Strictly forbidden |
| 4 | **Reserved Words** | `name` | Error | Cannot use `anthropic` or `claude` |
| 5 | **Gerund Advisory** | `name` | Advisory | Suggests gerund form (e.g., `processing-pdfs`) |
| 6 | **Description Length** | `description` | Error | Max 1,024 characters |
| 7 | **No XML Tags** | `description` | Error | Strictly forbidden |
| 8 | **Perspective Enforcement** | `description` | Warning | Must be third-person; avoids `I`, `me`, `my`, `we`, `our`, `you`, `your` |
| 9 | **Directory Naming** | File structure | Error | `name` must match parent folder name exactly |
| 10 | **Trigger Phrases** | `description` | Warning | Requires positive (`Use when...`) and negative (`Don't use for...`, `avoid`) triggers |
| 11 | **Action Verbs** | `description` | Warning | Must start with or contain active verbs (e.g., `creates`, `analyzes`, `validates`) |
| 12 | **Lean Context Body** | File content | Warning | Body of SKILL.md must not exceed 500 lines (progressive disclosure) |

---

## Agent Skill Structure Standards

Every compliant agent skill must follow this exact directory layout:

```
skill-name/
├── SKILL.md                    # Required: Metadata + core instructions (<500 lines)
├── scripts/                    # Tiny CLI tools for deterministic operations
│   ├── script-name.py
│   └── helper.sh
├── references/                 # Supplementary context (one level deep only)
│   ├── api-spec.md
│   └── auth-flow.md
└── assets/                     # Templates and static resources
    ├── output-template.json
    └── schema.yaml
```

### File Roles

- **SKILL.md**: The "brain." Contains YAML frontmatter (name, description) and imperative procedures. Keeps context lean by referencing external files.
- **scripts/**: Single-purpose CLI tools for fragile operations (regex parsing, API calls, validation). Not for shared library code.
- **references/**: One-level-deep supplementary files. Examples: API specifications, authentication flows, error code mappings, schemas.
- **assets/**: Output templates (JSON, YAML), static configuration files, or schemas the agent reads and uses.

---

## Best Practices Implemented

### 1. Metadata Optimization for Discoverability
The `name` and `description` in the YAML frontmatter are the ONLY fields an agent sees before deciding to trigger a skill.

**Name Requirements:**
- 1–64 characters
- Lowercase letters, numbers, single hyphens only
- Must match parent directory name exactly
- Gerund form preferred (e.g., `creating-react-components`)

**Description Requirements:**
- Max 1,024 characters (context window conscious)
- Third-person imperative mood (no pronouns)
- Must include positive trigger phrases ("Use when...")
- Must include negative trigger phrases ("Don't use for...", "avoid", "not for")
- Must start with/contain action verbs

### 2. Progressive Disclosure (Context Window Management)
- Keep SKILL.md under 500 lines
- Move large schemas, templates, and rule sets to `references/` or `assets/`
- Instruct agents to read these files only when needed
- Example: "Read `references/api-spec.md` to identify the correct endpoint."

### 3. Determinism & Self-Correction
- Use numbered, chronological steps with clear decision trees
- Include explicit error handling sections
- Scripts provide `stdout` for success and `stderr` for failures
- Eliminate "hallucination gaps" where agents must guess

### 4. Third-Person Imperative Tone
All instructions use direct commands and third-person perspective:
- ✅ "Extract the query parameters from the request."
- ❌ "I will extract the parameters." / "You should extract the parameters."

---

## Getting Started

### For Skill Authors
1. **Clone/download** this repository
2. **Read** [skill/SKILL.md](skill/SKILL.md) - Step-by-step procedure for creating a skill
3. **Use** the template: Copy `skill/assets/SKILL.template.md` to your new skill directory
4. **Validate** your metadata:
   ```bash
   python skill/scripts/validate-metadata.py --skillToValidate path/to/your/SKILL.md
   ```
5. **Review** `skill/references/checklist.md` before deployment

### For Reviewers/Validators
1. **Batch validate** a skills directory:
   ```bash
   python skill/scripts/validate-metadata.py --skillFolder path/to/skills/
   ```
2. **Interactive testing**: Run the TUI for ad-hoc validation:
   ```bash
   python skill/scripts/validate-metadata.py
   ```

### For Integration
- The validator can be integrated into CI/CD pipelines by parsing its `PASS`/`FAIL` exit codes and JSON output.
- Return codes: `0` = all checks passed, non-zero = failures detected.

---

## Key Artifacts

| File | Purpose | Usage |
|------|---------|-------|
| `README.md` | Full documentation, validator guide, and best practices | Reference for detailed rules and examples |
| `skill/SKILL.md` | Step-by-step skill authoring procedure | Follow to create new skills from scratch |
| `skill/assets/SKILL.template.md` | Boilerplate for new skills | Copy as starting point for new skill directories |
| `skill/references/checklist.md` | Pre-deployment audit checklist | Final manual review before pushing to production |
| `skill/scripts/validate-metadata.py` | Automated compliance engine | Run to validate skill metadata and structure |
| `linkedin-speach.md` | Public-facing article about the project | Marketing/awareness content |

---

## Why This Matters

**Deterministic agent routing and context window efficiency** are the difference between high-performing agents and hallucinating token-wasters.

### The Problem
- Agents often receive poorly structured instructions that waste context window
- Skill discovery is unpredictable when naming and descriptions are inconsistent
- Large, unstructured skill instructions force agents to guess and hallucinate

### The Solution
- **Automated validation** guarantees every skill adheres to best practices
- **Progressive disclosure** ensures agents get exactly the instructions they need, exactly when they need them
- **Strict naming and triggers** make skill routing deterministic and predictable
- **Lean context** maximizes LLM reasoning capacity

---

## Technical Details

### Dependencies
- Python 3.8+ (for `validate-metadata.py`)
- No external library dependencies (uses only Python standard library)

### Validation Output
The validator provides:
- **Color-coded terminal output** (Pass/Fail/Warning/Advisory)
- **JSON reports** (for CI/CD integration)
- **Detailed error messages** with suggestions for fixes

### Extensibility
The validator is designed to be extended:
- Add new compliance checks by extending the `Validator` class
- Add new output formats (e.g., XML, CSV) via formatter plugins
- Integrate with GitHub Actions, GitLab CI, or other automation platforms

---

## Learning Path

1. **Understand the Problem**: Read `README.md` to grasp why Agent Skills need structure
2. **Learn the Process**: Follow `skill/SKILL.md` step-by-step to author your first skill
3. **Build by Template**: Use `skill/assets/SKILL.template.md` as your starting point
4. **Validate**: Run `skill/scripts/validate-metadata.py` on your skill
5. **Audit**: Cross-check your skill against `skill/references/checklist.md`
6. **Deploy**: Push your validated skill to your agent platform

---

## Contributing

When contributing to this repository:
1. Validate all modifications with `validate-metadata.py`
2. Ensure all SKILL.md files stay under 500 lines
3. Follow third-person imperative tone throughout
4. Add new compliance checks to the validator with clear error messages
5. Update this `context.md` if changing project structure or goals

---

## Notes for Future Maintainers

- The validator is the core asset; keep it well-tested
- The checklist in `references/checklist.md` must stay synchronized with the 12 automated checks
- Keep templates (`assets/SKILL.template.md`) simple and minimal
- The README serves as the "complete manual"; context.md is the architectural overview
- Monitor agent platform updates for new best-practice guidelines and incorporate them into the validator

