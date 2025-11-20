# Additional Analysis for Enhanced Paper Impact

## Overview
This document outlines additional analyses that would significantly strengthen the MSR 2026 paper and provide deeper insights into AI agent library usage patterns.

---

## Priority 1: Agent-Specific Analysis (HIGH IMPACT) ⭐⭐⭐

### Motivation
The dataset includes 5 different AI agents with varying architectures and training:
- **OpenAI Codex** (16,487 PRs) - Older model, trained on GitHub
- **Devin** (3,811 PRs) - Autonomous agent
- **Copilot** (2,204 PRs) - IDE-integrated
- **Cursor** (1,010 PRs) - IDE-focused
- **Claude Code** (290 PRs) - Recent, conversational

Different agents may exhibit different library usage patterns based on their training data, architecture, and design philosophy.

### Research Question
**RQ5: How does library usage vary across different AI coding agents?**

### Analysis Required

#### 1. Per-Agent Statistics for RQ1-4
For each agent, calculate:
- % PRs adding new libraries
- % PRs modifying dependency files
- Stdlib vs external ratio
- Avg libraries per PR
- % with version specifications
- Version operator preferences
- Top 10 most common libraries

**Expected findings:**
- Codex may be more conservative (older training data)
- Claude Code may use newer libraries
- Copilot might favor Microsoft ecosystem libraries
- Devin might show more experimental behavior (autonomous)

**Implementation:**
```python
# Group by agent and language
for agent in ['OpenAI_Codex', 'Devin', 'Copilot', 'Cursor', 'Claude_Code']:
    for lang in ['Go', 'Python', 'TypeScript']:
        agent_lang_prs = results[(results['agent'] == agent) &
                                  (results['language'] == lang)]
        # Calculate all RQ1-4 metrics
```

**Output:**
- Table: "Library Usage Patterns by Agent and Language"
- Figure: Grouped bar chart comparing agents
- Insight paragraph for each agent's behavior

**Estimated effort:** 4 hours (coding) + 3 hours (analysis/writing)

---

#### 2. Agent-Specific Library Preferences
Identify unique and shared libraries across agents:
- Which libraries are used by all agents? (universal)
- Which are agent-specific? (unique preferences)
- Overlap analysis (Jaccard similarity)

**Expected findings:**
- All agents use common libraries (pytest, react, testing frameworks)
- Some agents may favor specific libraries (e.g., Claude Code using anthropic SDK)
- Clustering of agent behaviors

**Implementation:**
```python
# For each agent, get set of libraries used
agent_libs = {}
for agent in agents:
    agent_libs[agent] = set(all libraries used in PRs)

# Calculate overlaps
universal = set.intersection(*agent_libs.values())
unique = {agent: libs - universal for agent, libs in agent_libs.items()}
```

**Output:**
- Venn diagram (if 3-4 agents) or UpSet plot (if 5 agents)
- Table: "Agent-Specific Library Preferences"

**Estimated effort:** 3 hours

---

## Priority 2: Library Validation (MEDIUM-HIGH IMPACT) ⭐⭐½

### Motivation
A critical quality concern: Do agents ever hallucinate or misname libraries? This could lead to failed builds and developer frustration.

### Research Question
**RQ6: Do AI agents introduce invalid or non-existent library dependencies?**

### Analysis Required

#### 1. Validate Against Package Registries
For each library mentioned, check if it exists:
- **Python**: PyPI API (https://pypi.org/pypi/{package}/json)
- **JavaScript/TypeScript**: npm API (https://registry.npmjs.org/{package})
- **Go**: Go packages API or module proxy

**Implementation steps:**
1. Extract all unique libraries from results
2. Query package registries (with rate limiting)
3. Classify as: valid, invalid, ambiguous (e.g., private packages)
4. Calculate error rate per agent and language

**Expected findings:**
- Very low error rate (<1%) for mainstream agents
- Possible typos or outdated package names
- Private/internal packages may appear as "invalid"

**Implementation:**
```python
import requests
import time

def validate_python_package(package_name):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json",
                                timeout=5)
        return response.status_code == 200
    except:
        return False

def validate_npm_package(package_name):
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}",
                                timeout=5)
        return response.status_code == 200
    except:
        return False

# Validate all libraries with rate limiting
invalid_libs = []
for lib in unique_libraries:
    if lang == 'Python' and not validate_python_package(lib):
        invalid_libs.append((lib, 'Python'))
    time.sleep(0.1)  # Rate limit
```

**Output:**
- Table: "Invalid Library Detection Results"
- Examples of invalid libraries (if any found)
- Analysis of error types (typos, outdated names, hallucinations)

**Estimated effort:** 8 hours (implementation) + 2 hours (analysis)

**Note:** This adds a strong quality/reliability angle to the paper.

---

## Priority 3: Dependency File Patterns (MEDIUM IMPACT) ⭐⭐

### Motivation
Understanding *how* agents modify dependency files (not just *what* they add) reveals their development practices.

### Research Question
**RQ7: What patterns emerge in how AI agents modify dependency files?**

### Analysis Required

#### 1. Dependency File Change Patterns
Analyze the types of modifications:
- Adding new dependencies
- Updating existing versions
- Removing dependencies
- Reformatting/reorganizing
- Adding/modifying comments

**Implementation:**
```python
# For each PR with dep file changes
for pr in prs_with_dep_changes:
    old_deps = extract_deps_from_patch(pr, 'before')
    new_deps = extract_deps_from_patch(pr, 'after')

    added = new_deps - old_deps
    removed = old_deps - new_deps
    updated = [d for d in old_deps if d in new_deps but version_changed(d)]

    # Classify the change type
```

**Output:**
- Pie chart: Distribution of change types (add/update/remove/reformat)
- Finding: "X% of dependency changes are version updates rather than new additions"

**Estimated effort:** 4 hours

---

#### 2. Version Update Patterns
When agents update versions, how do they do it?
- Major version updates (2.x → 3.x)
- Minor version updates (1.2.x → 1.3.x)
- Patch version updates (1.0.1 → 1.0.2)
- Exact to range conversions (==1.0 → >=1.0)

**Expected findings:**
- Agents prefer conservative updates (patch > minor > major)
- Version range broadening for flexibility

**Estimated effort:** 3 hours

---

## Priority 4: Code Import vs Dependency File Discrepancy (MEDIUM IMPACT) ⭐⭐

### Motivation
Do agents always update dependency files when they import new libraries? Missing this step leads to broken builds.

### Research Question
**RQ8: How often do AI agents import libraries without adding them to dependency files?**

### Analysis Required

#### 1. Detect Import-Dependency Mismatches
For each PR:
- Libraries imported in code files
- Libraries declared in dependency files
- Mismatch: imported but not declared

**Implementation:**
```python
for pr in results:
    imported = set(pr['libraries_in_code'])
    declared = set(pr['libraries_in_deps'])

    # Exclude stdlib
    imported_external = imported - stdlib_for_language(pr['language'])

    # Missing from dependency file
    missing = imported_external - declared

    if missing:
        mismatches.append((pr['pr_id'], missing))
```

**Expected findings:**
- Low mismatch rate (agents are generally good at this)
- Some languages may have higher rates (e.g., Go with implicit dependencies)
- Possible finding: "0.5% of PRs import libraries without declaring them"

**Output:**
- Table: Mismatch rates per language
- Discussion: Implications for build reliability

**Estimated effort:** 3 hours

---

## Priority 5: Testing Library Usage (MEDIUM-LOW IMPACT) ⭐½

### Motivation
Testing is a critical software engineering practice. How do agents handle test dependencies?

### Research Question
**RQ9: How do AI agents use testing libraries compared to production libraries?**

### Analysis Required

#### 1. Classify Libraries by Purpose
Categorize libraries as:
- Testing frameworks (pytest, jest, vitest, testify)
- Production libraries (pandas, react, gin)
- Development tools (eslint, black, golangci-lint)

**Implementation:**
```python
test_libs = {'pytest', 'unittest', 'jest', 'vitest', 'mocha', 'testify', ...}
dev_libs = {'eslint', 'black', 'prettier', ...}

for lib in all_libraries:
    if lib in test_libs:
        category = 'testing'
    elif lib in dev_libs:
        category = 'dev'
    else:
        category = 'production'
```

**Output:**
- Pie chart: Distribution of library types
- Finding: "X% of agent-introduced libraries are for testing"

**Estimated effort:** 2 hours

---

## Priority 6: Temporal Trends (LOW-MEDIUM IMPACT) ⭐

### Motivation
Agent behavior may evolve over time as models improve.

### Research Question
**RQ10: How has AI agent library usage evolved over time?**

### Analysis Required

#### 1. Time-Series Analysis
Plot library adoption rate over time (by PR created_at date):
- % PRs adding new libraries per month
- New unique libraries introduced per month
- Version specification adoption over time

**Prerequisites:**
- Need PR creation dates from pull_request.parquet
- Group by year-month

**Expected findings:**
- Steady or increasing adoption
- Newer agents (Claude Code) may show different patterns
- Possible seasonality effects

**Output:**
- Line chart: Library adoption trends over time
- Finding: "Agent library usage has increased X% year-over-year"

**Estimated effort:** 4 hours

---

## Priority 7: Repository Context Analysis (LOW IMPACT) ⭐

### Motivation
Do agents adapt to existing project conventions?

### Research Question
**RQ11: Do AI agents match the library usage patterns of their host repositories?**

### Analysis Required

#### 1. Compare Agent PRs to Existing Code
For each repository:
- Libraries used before agent PR
- Libraries introduced by agent PR
- Match rate: agent uses existing vs introduces new

**Challenges:**
- Requires analyzing non-agent code in repositories
- Computationally expensive
- May not have pre-PR snapshots in dataset

**Expected findings:**
- Agents mostly use existing libraries
- When they introduce new ones, they're typically related to existing stack

**Estimated effort:** 12+ hours (significant data collection needed)

**Recommendation:** Skip unless targeting a journal version or extended paper

---

## Visualization Recommendations

### High-Impact Visualizations (Priority)

1. **Agent Comparison Heatmap** (RQ5)
   - Rows: Agents (5)
   - Columns: Metrics (% new libs, % with versions, avg libs/PR)
   - Color: Intensity (green = high, red = low)
   - **Impact**: Shows clear agent differences at a glance

2. **Grouped Bar Chart: Agents × Languages** (RQ5)
   - X-axis: Language (Go, Python, TypeScript)
   - Y-axis: % PRs adding new libraries
   - Groups: Agents (5 bars per language)
   - **Impact**: Shows interaction between agent and language

3. **Sankey Diagram: Import → Dependency Flow** (RQ8)
   - Left: Libraries imported in code
   - Right: Libraries in dependency files
   - Flows: Show which are matched vs mismatched
   - **Impact**: Visually striking, shows data quality

4. **Time Series: Library Adoption Trends** (RQ10)
   - X-axis: Time (months)
   - Y-axis: % PRs adding new libraries
   - Lines: Each agent or language
   - **Impact**: Shows evolution and trends

### Medium-Impact Visualizations

5. **UpSet Plot: Agent Library Overlaps** (RQ5)
   - Shows which libraries are shared/unique across agents
   - Better than Venn diagram for 5 sets
   - **Impact**: Shows agent clustering behavior

6. **Treemap: Library Categories** (RQ9)
   - Boxes: Library categories (testing, production, dev)
   - Size: Frequency of use
   - Color: Category type
   - **Impact**: Shows library purpose distribution

---

## Recommended Analysis Priority for Paper

### Must-Do (For 4-page paper)
1. ✅ **RQ5: Agent-specific analysis** (4 hours) - Already have data, just need to analyze
   - Adds significant insight without new data collection
   - Differentiates from prior work
   - Fits well in existing structure

### Should-Do (If time permits / for stronger paper)
2. ⚠️ **RQ6: Library validation** (10 hours)
   - Adds quality/reliability angle
   - Novel contribution
   - Requires API calls (can be done in parallel with writing)

3. ⚠️ **RQ8: Import-dependency mismatches** (3 hours)
   - Practical developer concern
   - Quick to implement with existing data
   - Adds actionable insight

### Nice-to-Have (For journal extension or future work)
4. **RQ7: Dependency file patterns** (4 hours)
5. **RQ9: Testing library usage** (2 hours)
6. **RQ10: Temporal trends** (4 hours)

### Skip (Unless extending to journal paper)
7. **RQ11: Repository context** (12+ hours)

---

## Implementation Strategy

### Phase 1: Agent Analysis (This Week)
- [ ] Extract agent from PR data (already in results)
- [ ] Calculate per-agent statistics for RQ1-4
- [ ] Create agent comparison visualizations
- [ ] Write RQ5 results section (0.3 pages)

### Phase 2: Library Validation (Next Week)
- [ ] Implement package registry validators
- [ ] Validate all unique libraries (with caching)
- [ ] Analyze error patterns
- [ ] Write RQ6 results section (0.2 pages)

### Phase 3: Mismatch Analysis (Optional)
- [ ] Implement import-dependency comparison
- [ ] Analyze mismatch patterns
- [ ] Add to Discussion section (0.1 pages)

---

## Data Availability

### Already Available (No New Data Needed)
- ✅ Agent information (in PR data)
- ✅ Import vs dependency separation (in analysis results)
- ✅ Version information (in analysis results)
- ✅ PR creation dates (in pull_request.parquet)

### Requires API Calls
- ⚠️ Package registry validation (PyPI, npm, Go packages)
- Can cache results to avoid re-querying
- Estimated time: ~2-4 hours for all packages

### Requires Additional Dataset Processing
- ❌ Pre-PR code state (not easily available)
- ❌ Non-agent PRs for comparison (separate analysis needed)

---

## Page Budget Considerations

With 4 strict pages:
- Adding RQ5 (agent comparison): +0.3 pages (worth it)
- Adding RQ6 (validation): +0.2 pages (worth it)
- Adding RQ7-11: +0.1-0.2 pages each (tight)

**Recommendation:**
- Include RQ5 (agent comparison) as primary addition
- Include RQ6 (validation) if time permits before deadline
- Mention RQ7-11 in "Future Work" section

---

## Questions for Discussion

1. **Agent comparison (RQ5)**: Should we focus on differences or similarities?
2. **Invalid libraries (RQ6)**: What threshold defines "invalid" (404, timeout, private)?
3. **Paper focus**: Breadth (more RQs) or depth (fewer RQs, more analysis)?
4. **Target venue**: Mining Challenge only, or aim for main track if results strong?

---

*Last updated: November 20, 2025*
*Status: Ready for implementation*
