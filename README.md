# Agent Skills: Design Best Practices & Validation Toolkit

This repository provides a professional-grade guide and an automated validation toolkit for authoring Agent Skills that comply with the `agentskills.io` specification and optimal LLM discoverability guidelines.

Originally created as a conceptual guide by [@mgechev](https://github.com/mgechev/), this repository has been refactored, fixed, and extensively expanded. The original implementation was non-functional upon initial cloning; it has been rebuilt from scratch into a fully operational validation suite.

This version specifically fixes the original workflow and expands it by adding:

1. Support for validating a standalone skill name and description.
2. An option to validate a complete `SKILL.md` file using YAML frontmatter.
3. A folder-scanning mode to validate an entire directory of skills.
4. A retro terminal menu so users can choose which validation mode to run.
5. Full coverage of all official best practices from Claude's Agent Skills guidelines, beyond the initial 5 basic checks.

It now supports multiple testing interfaces (including a retro terminal menu) and implements 100% of the best practices recommended by [Anthropic / Claude's official guidelines](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

This README has been updated to reflect the recent implementation changes and the validation improvements discussed during design review.

---

## Automated Validation Toolkit (`validate-metadata.py`)

A robust metadata validator is provided in [validate-metadata.py](file:///c:/Crisarch/Programming/skills-best-practices-cn/skills-best-practices/skill/scripts/validate-metadata.py). This tool enforces compliance with naming, description, styling, and progressive disclosure rules before deploying skills.

### Supported Execution Modes

The script supports four operational modes, and now exposes the three main validation flows by default through an interactive menu.

#### 1. Old-School Interactive Menu (TUI)
If run without any arguments, the script launches an interactive terminal dashboard. This enables quick ad-hoc testing:
```bash
python skill/scripts/validate-metadata.py
```
```text
========================================================
     SKILL METADATA VALIDATOR - Interactive Mode
========================================================
  [1]  Validate a simple description
  [2]  Validate a .md file (YAML frontmatter)
  [3]  Validate an entire folder of skills
  [4]  List folder / sub-folder structure
  [q]  Quit
========================================================
```

##### How to use the menu
1. Run the script with no arguments.
2. Choose `1` to validate a standalone skill name and description.
3. Choose `2` to validate a full `SKILL.md` file by parsing its YAML metadata.
4. Choose `3` to validate an entire folder containing multiple skill directories.
5. Choose `4` to print an ASCII tree of a folder's structure (up to three levels deep).
6. Choose `q` to exit the menu.

Example:
```text
> python skill/scripts/validate-metadata.py
Select an option: 2
Enter path to SKILL.md: skill/SKILL.md
```

#### 2. File Validation Mode
Extracts the `name` and `description` directly from a markdown file's YAML frontmatter, validating both fields and checking that the file body length does not exceed recommended limits:
```bash
python skill/scripts/validate-metadata.py --skillToValidate path/to/SKILL.md
```

#### 3. Batch Folder Validation Mode
Scans a folder containing multiple skill subdirectories. It searches for all `.md` files (such as `SKILL.md` in each subdirectory) and evaluates them in a single batch, outputting a clear `PASS`/`FAIL` report:
```bash
python skill/scripts/validate-metadata.py --skillFolder path/to/skills/
```

#### 4. Direct CLI Mode
Validates a standalone skill name and description provided directly via command-line arguments:
```bash
python skill/scripts/validate-metadata.py --name "my-skill" --description "Enables X. Use when Y. Don't use for Z."
```

#### 5. Folder Structure Listing Mode
Prints an ASCII directory tree of a folder (up to three levels deep). Useful for inspecting skill directory layouts:
```bash
python skill/scripts/validate-metadata.py --listStructure path/to/folder/
```

---

## Validation Test Matrix

Every mode is tested against the `test/` directory (shipped with the repo) to confirm correct behavior across normal, edge, and failure cases.

| Menu | Mode / CLI Flag | Test Target | Expected Result | Verified |
|------|----------------|-------------|----------------|----------|
| [1] | `--name` + `--description` | `testing-validator` / valid description | PASS (exit 0) | ✓ |
| [2] | `--skillToValidate` | `test/valid-skill.md` | Advisory + mismatch (exit 1) | ✓ |
| [2] | `--skillToValidate` | `test/invalid-skill.md` | 9 errors detected (exit 1) | ✓ |
| [3] | `--skillFolder` | `test/skills/` | 2 PASS, 0 FAIL (exit 0) | ✓ |
| [4] | `--listStructure` | `test/` | Full tree printed (exit 0) | ✓ |
| — | `q` | Quit immediately | "Goodbye!" (exit 0) | ✓ |
| — | Invalid choice | `x` then `q` | Error message, loops back | ✓ |
| — | Empty folder | `--skillFolder test/empty-folder/` | No `.md` files found (exit 1) | ✓ |
| — | Missing args | `--name only-name` | Usage error (exit 2) | ✓ |

Run the full suite yourself:
```bash
python skill/scripts/validate-metadata.py --listStructure test
python skill/scripts/validate-metadata.py --skillToValidate ../../test/valid-skill.md
python skill/scripts/validate-metadata.py --skillToValidate ../../test/invalid-skill.md
python skill/scripts/validate-metadata.py --skillFolder ../../test/skills
```

---

## The 12 Automated Compliance Checks

The validator automatically executes 12 separate checks to guarantee complete alignment with best practices:

### Already covered by this toolkit

- Name length 1–64 chars
- Name: lowercase, numbers, single hyphens only
- Description max 1,024 chars
- Third-person perspective (basic heuristic)
- Directory name matches name field
- Positive trigger phrase ("Use when...")
- Negative trigger phrase ("Don't use for...")

This version also adds the remaining missing checks from Claude's skill best practices, achieving full coverage.

| # | Check Name | Target Field | Severity | Rule Description |
|---|---|---|---|---|
| **1** | **Name Length** | `name` | **Error** | Must be between 1 and 64 characters. |
| **2** | **Character Rules** | `name` | **Error** | Use only lowercase letters, numbers, and single hyphens. No consecutive hyphens; cannot start/end with hyphens. |
| **3** | **No XML Tags** | `name` | **Error** | XML tags (`<...>`) are strictly prohibited in the name field. |
| **4** | **Reserved Words** | `name` | **Error** | The terms `anthropic` and `claude` are reserved and cannot be used. |
| **5** | **Gerund Advisory** | `name` | *Advisory* | Suggests using the gerund form (e.g., `processing-pdfs`) for clarity and action-driven naming. |
| **6** | **Description Length** | `description` | **Error** | Must be 1,024 characters or fewer. |
| **7** | **No XML Tags** | `description` | **Error** | XML tags (`<...>`) are strictly prohibited in the description field. |
| **8** | **Perspective Enforcement** | `description` | *Warning* | Ensures third-person style by alerting if pronouns like `I`, `me`, `my`, `we`, `our`, `you`, or `your` are found. |
| **9** | **Directory Naming** | File Structure | **Error** | The `name` field in the frontmatter must exactly match the parent folder's name (e.g., `angular-testing/SKILL.md` must have `name: angular-testing`). |
| **10**| **Trigger Phrases** | `description` | *Warning* | Requires a positive trigger phrase (`Use when...`) and a negative trigger phrase (`Don't use for...`, `do not use`, `avoid`, or `not for`). |
| **11**| **Action Verb Presence** | `description` | *Warning* | Ensures the description starts with or contains active verbs (e.g., `creates`, `analyzes`, `validates`, `checks`). |
| **12**| **Lean Context Body** | File Content | *Warning* | Checks the main body of `SKILL.md` (excluding frontmatter) and warns if it exceeds 500 lines to enforce progressive disclosure. |

---

## Structure of a Skill

Every skill must follow this directory structure:

```text
skill-name/
├── SKILL.md              # Required: Metadata + core instructions (<500 lines)
├── scripts/              # Executable code (Python/Bash) designed as tiny CLIs
├── references/           # Supplementary context (schemas, cheatsheets) 
└── assets/               # Templates or static files used in output
```

*   **`SKILL.md`**: Acts as the "brain." Use it for high-level procedures and navigation commands.
*   **`references/`**: Supplementary documentation and schemas. Keep them exactly **one level deep** only. Link directly to them from `SKILL.md`.
*   **`scripts/`**: Executable code for fragile or repetitive operations where variation is a bug. **Do not bundle library code here**.
*   **`assets/`**: Output templates, static resources, or JSON schemas that the agent can read and copy.

---

## Core Skill Design Principles

### 1. Optimize Frontmatter for Discoverability
The `name` and `description` in the frontmatter of `SKILL.md` are the only elements an agent sees before deciding to trigger a skill.
*   **Adhere to Strict Naming**: Must match the parent directory name, be lowercase, alphanumeric, and use single hyphens only.
*   **Write Trigger-Optimized Descriptions**: Max 1,024 characters. Focus on high-relevance trigger phrases to prevent routing issues.
    *   *Suboptimal*: `"React skills."` (Too vague).
    *   *Optimal*: `"Creates and builds React components using Tailwind CSS. Use when the user wants to update component styles or UI logic. Don't use it for Vue, Svelte, or vanilla CSS projects."`

### 2. Progressive Disclosure & Resource Management
Maintain a clean context window by loading information only when needed.
*   **Keep SKILL.md Lean**: Limit the main file to **under 500 lines**. Offload details to subdirectories.
*   **Use Flat Subdirectories**: Move bulky context to standard folders. Keep files exactly **one level deep** (e.g., `references/schema.md`, not `references/db/v1/schema.md`).
*   **Just-in-Time (JiT) Loading**: Explicitly command the agent when to read a file. The agent will not see these resources until you direct it to do so (e.g., *"Read references/auth-flow.md to identify specific error codes"*).
*   **Explicit Pathing**: Always use **relative paths** with forward slashes (`/`), regardless of the host operating system.

### 3. Exclude Human-Centric Documentation
Skills are authored for autonomous agents, not human developers. To prevent unnecessary token consumption and clutter:
*   Do **NOT** create `README.md`, `CHANGELOG.md`, or `INSTALLATION_GUIDE.md` inside a skill directory.
*   Do **NOT** write redundant logic that the agent already handles reliably.
*   Do **NOT** bundle long-lived library code inside a skill. Library code belongs in the host repository's standard CLI or module folders.

### 4. Direct Procedural Instructions over Prose
*   **Step-by-Step Numbering**: Outline workflows as a strict chronological sequence. Explicitly map out branches or decision trees (e.g., *"Step 2: If source maps are required, run `ng build --source-map`. Otherwise, skip to Step 3."*).
*   **Provide Concrete Templates**: Instead of paragraphs describing formatting, place a clean template in `assets/` and instruct the agent to copy its structure.
*   **Third-Person Imperative Mood**: Command the agent directly (e.g., *"Extract the text..."* rather than *"I will extract..."* or *"You should extract..."*).
*   **Specific & Consistent Terminology**: Stick to domain-native terms consistently (e.g., use the term "template" instead of interchangeably using "html", "markup", or "view" in an Angular skill).

### 5. Deterministic Scripts for Repetitive Operations
*   **Offload Fragile Operations**: Rather than asking the LLM to write complex parsing scripts from scratch, bundle tested scripts in the `scripts/` directory.
*   **Descriptive Outputs**: Ensure scripts exit with highly descriptive `stdout` for successful operations and `stderr` for failures, enabling the agent to self-correct without human intervention.

---

## Collaboration with LLMs (Manual Validation Guide)

In addition to the automated validator script, testing skills in collaboration with LLMs is recommended to ensure they are useful and regression-free. Evals can be designed with inspiration from benchmarks like [SkillsBench](https://arxiv.org/abs/2602.12670).

### Phase 1: Discovery Validation
Tests how an LLM interprets a description in isolation to prevent false routing. Paste this prompt into a fresh chat:

> I am building an Agent Skill based on the agentskills.io spec. Agents will decide whether to load this skill based entirely on the YAML metadata below.
>
> ```yaml
> name: angular-vite-migrator
> description: Migrates Angular CLI projects from Webpack to Vite and esbuild. Use when the user wants to update builder configurations, replace webpack plugins with rollup equivalents, or speed up Angular compilation. Don't use for React, Vue, or Svelte migrations.
> ```
>
> Based strictly on this description:
> 1. Generate 3 realistic user prompts that you are 100% confident should trigger this skill.
> 2. Generate 3 user prompts that sound similar but should NOT trigger this skill (e.g., migrating a React app to Vite, or just updating Angular versions).
> 3. Critique the description: Is it too broad? Suggest an optimized rewrite.

### Phase 2: Logic & Monologue Validation
Ensures instructions are completely deterministic. Feed the LLM the entire directory structure and `SKILL.md`:

> Here is the full draft of my SKILL.md and the directory tree of its supporting files:
> 
> ```text
> ├── SKILL.md
> ├── scripts/esbuild-optimizer.mjs
> └── assets/vite.config.template.ts
> ```
> 
> [Paste SKILL.md content here]
> 
> Act as an autonomous agent that has just triggered this skill. Simulate your execution step-by-step based on a request to "Migrate my Angular v17 app to Vite".
>
> For each step, write out your internal monologue:
> 1. What exactly are you doing?
> 2. Which specific file or script are you reading or running?
> 3. Flag any Execution Blockers: Point out the exact line where you are forced to guess or hallucinate because instructions are ambiguous.

### Phase 3: Adversarial Edge-Case Testing
Prompts the LLM to locate vulnerabilities or missing fallbacks:

> Act as a ruthless QA tester. Your goal is to break this skill.
> Ask me 3 to 5 highly specific, challenging questions about edge cases, failure states, or missing fallbacks in the SKILL.md. Focus on:
>
> * What if `scripts/esbuild-optimizer.mjs` fails due to a legacy CommonJS dependency?
> * What if the user's `angular.json` contains heavily customized Webpack builders (`@angular-builders/custom-webpack`) that Vite doesn't support?
> * Are there implicit assumptions made about the user's Node environment?
>
> Do not fix these issues yet. Just ask me the numbered questions and wait for me to answer them.

### Phase 4: Progressive Disclosure Restructuring
Have the LLM incorporate the feedback while refactoring:

> Based on my answers to your edge-case questions, rewrite the SKILL.md file, strictly enforcing the Progressive Disclosure design pattern:
>
> 1. Keep the main `SKILL.md` strictly as a high-level set of steps using third-person imperative commands (e.g., "Execute the esbuild script", "Read the Vite config template").
> 2. If there are dense rules, large config templates, or complex schemas currently in the file, remove them. Move them to a new file in `references/` or `assets/`, and replace the text in `SKILL.md` with a command to read that specific file only when needed.
> 3. Add a dedicated "Error Handling" section at the bottom incorporating my answers about Webpack fallbacks and CommonJS resolution.
