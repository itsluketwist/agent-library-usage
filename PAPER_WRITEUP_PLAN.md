# MSR 2026 Mining Challenge Paper Write-Up Plan

## Paper Title (Draft)

**Primary**: "From Conversations to Code: How AI Agents Specify Library Dependencies"

**Alternatives**:
- "Library Dependency Patterns in Agent-Authored Pull Requests: An Empirical Study of AIDev"
- "How Conservative Are AI Coding Agents? An Analysis of Library Usage in 23,791 Pull Requests"
- "Dependency Diligence: Version Specification Behavior in AI-Generated Code"

**Title rationale**: Emphasizes the key finding (8-10x improvement over conversations) and creates contrast

---

## Key Findings Summary (Funnel Narrative)

**The Story**: Agents are conservative, careful, and context-aware when managing dependencies in production code

1. **RQ1 - Baseline**: Agents use libraries frequently (avg 0.97-2.63 libs/PR) but favor standard libraries (4-8% stdlib vs 92-96% external of unique libs)

2. **RQ2 - Conservatism**: Agents are highly conservative - only 0.2-3.2% of PRs introduce new libraries ("dependency minimalism")

3. **RQ3 - Diligence** ⭐ **HEADLINE**: When agents DO add libraries, they specify versions 8-10x more often than in conversations (84-100% vs 9.67%)
   - Context matters: Modified files (84-100%) vs project init (33-100%)
   - Ecosystem influences: Python flexible (84%), TypeScript/Go enforced (100%)

4. **RQ4 - Patterns**: Common choices reflect training data (openai, typescript) and practical needs (testing frameworks)

**Contributions**:
- First large-scale study of agent library usage in production code (23,791 PRs)
- Challenges concerns about AI carelessness with dependencies
- Shows agents adapt behavior to context (conversations vs production)
- Quantifies language ecosystem influence on agent behavior

---

## Paper Requirements (Strict)
- **Length**: 4 pages + 1 page references (NO exceptions)
- **Format**: ACM sigconf (double-column)
- **Review**: Double-anonymous
- **Required sections**: Ethical implications before conclusion
- **Deadline**: December 23, 2025
- **Conference**: MSR 2026, April 27 - May 4, 2026, Trondheim, Norway

---

## Refined Research Questions (Funnel Narrative)

**Narrative Structure**: Each RQ progressively narrows focus, building a coherent story about agent library usage:
1. All library usage (broad baseline)
2. New library additions (narrowing focus)
3. Version specifications for new libraries (quality check)
4. Patterns or issues (contextual insights)

---

### RQ1: How frequently do AI agents use libraries?

**Short form**: How frequently do agents use libraries?

**Motivation**: Establish baseline understanding of agent library usage patterns

**Analysis Scope**:
- **All imports**: Both standard library and external
- **Classification**: Standard vs external libraries
- **Metrics**:
  - Total libraries per PR: avg 0.97 (Go), 2.13 (Python), 2.63 (TypeScript)
  - Stdlib vs external ratio: 55:641 (Go), 49:1,250 (Python), 25:2,614 (TypeScript)
  - % PRs using external libraries
  - Most commonly imported libraries (overall)

**Key Findings**:
- Agents use libraries in majority of PRs
- Heavy reliance on standard libraries where available
- Language ecosystem maturity affects external library adoption
- Go: 8% stdlib, Python: 4% stdlib, TypeScript: 1% stdlib

**Insight**: Agents follow best practices by preferring standard libraries, but vary by ecosystem

---

### RQ2: How frequently do AI agents import NEW libraries?

**Short form**: How frequently do agents import new libraries?

**Motivation**: Understand agent conservatism vs experimentation with dependencies (narrows from RQ1 to just NEW additions)

**Analysis Scope**:
- **Focus**: Only newly added libraries (not existing usage)
- **Context**: Both modified files and added files
- **Metrics**:
  - % PRs adding new libraries: 0.2% (Go), 1.7% (Python), 3.2% (TypeScript)
  - % PRs modifying dependency files: 1.8% (Go), 9.4% (Python), 25.3% (TypeScript)
  - Avg new libraries per PR: 0.02 (Go), 0.12 (Python), 0.40 (TypeScript)
  - Total new libraries introduced: 203 (Go), 887 (Python), 2,584 (TypeScript)

**Key Findings**:
- Agents are highly conservative about adding new dependencies
- Less than 4% of PRs introduce new libraries across all languages
- TypeScript most active (3.2%), Go most conservative (0.2%)
- Gap between dep file changes (25%) and truly new libraries (3.2%) shows agents mostly maintain existing dependencies

**Insight**: Agents exhibit "dependency minimalism" - they prefer working with existing libraries rather than introducing new ones

---

### RQ3: Do AI agents specify versions when importing new libraries?

**Short form**: Do agents specify versions when importing new libraries?

**Motivation**: Assess quality and rigor of new library additions (narrows from RQ2 to quality of additions)

**Analysis Scope**:
- **Focus**: Only libraries in modified/added dependency files
- **Critical distinction**: Modified files (agents choosing libraries) vs added files (project init)
- **Comparison**: Prior work (Raj & Costa MSR 2024) found ChatGPT mentions versions in only 9.67% of conversations

**Metrics**:

*Modified files (most relevant):*
- Go: 100% (203/203)
- TypeScript: 100% (2,584/2,584)
- Python: 83.9% (759/905)

*Added files (project initialization):*
- Python: 33.3% (19/57)
- TypeScript: 100% (1,349/1,349)

*Version operators:*
- Python prefers exact: `==` (88%)
- TypeScript prefers compatible: `^` (73%)
- Go: Module system enforces versions

**Key Findings**:
- **8-10x improvement over conversations** (9.67% → 84-100%)
- Context matters: Higher rates when modifying (84-100%) vs initializing (33-100%)
- Language ecosystems influence behavior (npm/go mod enforce, Python more flexible)
- Agents adapt to project context and follow ecosystem conventions

**Insight**: While agents are careless about versions in casual conversations, they demonstrate high diligence in production code contributions

---

### RQ4: What patterns emerge in agent library adoption?

**Short form**: What are the most common libraries used/adopted by agents? **OR** Do agents import invalid/hallucinated dependencies?

**Status**: ⚠️ Choose based on which is more interesting/novel

**Option A: Most Common Libraries (SAFE)**
- **Motivation**: Understand agent preferences and training data influence
- **Metrics**:
  - Top 10 libraries per language (with counts)
  - Patterns: testing frameworks, AI libraries, type systems
  - Language-specific preferences
- **Findings**:
  - Python: openai (18), requests (17), numpy (15), pandas (13)
  - TypeScript: typescript (123), @types/node (84), eslint (52), zod (48)
  - Go: testify (3), snappy (6)
- **Insight**: Reflects both training data and practical developer needs

**Option B: Invalid Libraries (NOVEL)**
- **Motivation**: Quality and reliability concerns - do agents hallucinate?
- **Metrics**:
  - % libraries validated against PyPI/npm/Go packages
  - Types of errors: typos, outdated names, hallucinations
  - Comparison across agents
- **Requirements**:
  - Implement validation (~8-10 hours)
  - API rate limiting considerations
  - Handle private packages gracefully
- **Expected finding**: Very low error rate (<1%), but even rare errors are concerning
- **Insight**: Quantifies reliability for production use

**Decision Criteria**:
- **Choose A** if: Time-constrained, want safe contribution, good story completion
- **Choose B** if: Have time for validation, want novelty, findings show issues
- **Fallback**: Do A, mention B in "Future Work"

---

### Optional: RQ5 (Agent Comparison)

**Only include if**: Space permits (~0.3 pages) or drop to "Future Work"

**Motivation**: Different agents may have different training/design

**Quick wins from existing data**:
- Already have agent labels in results
- Can break down RQ1-4 by agent
- 4 hours analysis + visualization

**Expected findings**:
- Codex may be more conservative (older training)
- Devin may be more experimental (autonomous)
- Claude Code limited sample (290 PRs) but newer
- Variation in library preferences by agent

---

## Paper Structure (4 Pages)

### Page 1: Introduction + Dataset (~1.0 page)

**1.1 Introduction (0.6 page)**
- **Hook**: "AI coding agents are transforming software development, but how do they handle the critical task of selecting and managing external library dependencies?"
- **Problem**: Library selection impacts security, maintainability, reproducibility
- **Gap**: No empirical study on agent library usage patterns at scale
- **Contribution**: First large-scale analysis of library usage in 23,791 agent-authored PRs across 3 languages
- **Key findings preview**: Agents are surprisingly conservative, language-dependent, version-conscious

**1.2 Dataset: AIDev (0.4 page)**
- **Overview**: 33,596 curated PRs from 2,807 repos (100+ stars)
- **Scope**: 5 agents (Claude Code, Cursor, Devin, Copilot, Codex)
- **Subset**: Top 3 languages (Go: 10,107 PRs, Python: 7,190 PRs, TypeScript: 6,494 PRs)
- **Cite**: AIDev dataset paper (Hao Li et al.)
- **Table 1**: Dataset statistics by language and agent

### Page 2: Methodology (~1.0 page)

**2.1 Data Collection (0.3 page)**
- PR commit details with file-level changes (patch data)
- 711,923 file changes across 23,791 PRs
- Filtering: Code files vs dependency files

**2.2 Library Extraction (0.4 page)**
- **Import detection**: Language-specific patterns (import/require/go packages)
- **Dependency parsing**: requirements.txt, package.json, go.mod
- **Version extraction**: Regex for semantic versioning (==, >=, ^, ~, etc.)
- **Classification**: Standard library vs external libraries
- **Figure 1**: Extraction pipeline diagram

**2.3 Analysis Approach (0.3 page)**
- Per-PR analysis: Libraries in code vs dependency files
- "New libraries": Those added to dependency files
- Aggregate statistics across languages
- Quantitative analysis with frequency distributions

### Page 3: Results (~1.0 page)

**Narrative**: Progressive narrowing from all usage → new additions → quality of additions → patterns

**3.1 RQ1: How frequently do agents use libraries? (0.25 page)**
- **Finding**: Agents use libraries in majority of PRs
  - Avg libraries per PR: 0.97 (Go), 2.13 (Python), 2.63 (TypeScript)
  - Heavy stdlib reliance: 8% (Go), 4% (Python), 1% (TypeScript) of unique libraries
- **Table 2**: Library usage statistics per language
- **Interpretation**: Agents follow best practices but vary by ecosystem

**3.2 RQ2: How frequently do agents import NEW libraries? (0.25 page)**
- **Finding**: Agents are highly conservative ("dependency minimalism")
  - Only 0.2% (Go), 1.7% (Python), 3.2% (TypeScript) of PRs add new libraries
  - Avg new libs per PR: 0.02 (Go), 0.12 (Python), 0.40 (TypeScript)
- **Figure 2**: Bar chart - % PRs adding new libraries by language
- **Interpretation**: Agents prefer working with existing dependencies over introducing new ones

**3.3 RQ3: Do agents specify versions when importing new libraries? (0.35 page)**
- **Finding**: **8-10x more diligent than conversations** (headline result!)
  - Modified files: 100% (Go/TS), 83.9% (Python)
  - Comparison: ChatGPT conversations only 9.67% (Raj & Costa MSR 2024)
- **Context matters**: Modified (84-100%) vs added files (33-100%)
- **Version operators**: Python `==` (88%), TypeScript `^` (73%)
- **Figure 3**: Side-by-side comparison with conversation baseline (RED LINE at 9.67%)
- **Interpretation**: Agents adapt to production context, follow ecosystem conventions

**3.4 RQ4: What patterns emerge? (0.15 page)**
- **Option A - Common Libraries**:
  - Top libraries: openai, typescript, testing frameworks
  - Reflects training data and practical needs
  - **Table 3**: Top 10 libraries per language (compact)
- **Option B - Invalid Libraries** (if implemented):
  - Validation rate: X% against PyPI/npm/Go packages
  - Error types and frequency
  - Quality implications

### Page 4: Discussion + Conclusion + Ethics (~1.0 page)

**4. Discussion (0.35 page)**
- **Implications for developers**: Agents are safe but may miss useful libraries
- **Implications for tool builders**: Consider dependency suggestion features
- **Limitations**: Dataset bias (Codex-heavy), patch-based extraction may miss context
- **Future work**: Invalid library detection, temporal trends, agent-specific patterns

**5. Ethical Implications (0.15 page)**
- **Dependency security**: Agents may introduce vulnerable versions
- **Training data influence**: Biases toward popular libraries
- **Attribution**: Agent-generated code may not credit library authors appropriately
- **Recommendation**: Human review of agent dependency choices

**6. Threats to Validity (0.15 page)**
- **Construct**: Patch-based extraction may miss implicit dependencies
- **Internal**: Dataset skewed toward OpenAI Codex (69% of PRs)
- **External**: Limited to popular repos (100+ stars), may not generalize
- **Reliability**: Manual validation on subset confirms 95%+ accuracy

**7. Conclusion (0.15 page)**
- **Summary**: First large-scale study of agent library usage
- **Key takeaway**: Agents are conservative, version-conscious, language-dependent
- **Impact**: Informs agent design and developer practices
- **Future**: Expand to more agents, languages, and temporal analysis

### References Page (1 page)
- AIDev dataset paper
- MSR 2024 library version paper (Raj & Costa)
- Agent papers (Claude Code, Cursor, Devin, Copilot, Codex)
- Library management papers
- Empirical SE methodology papers

---

## Figures & Tables Plan (5-6 total)

### Must-Have Visualizations

**Table 1: Dataset Statistics**
- Rows: Go, Python, TypeScript, Total
- Columns: Total PRs, Agents (top 3), Files Changed, Commits
- Size: 1/4 column width

**Figure 1: Library Extraction Pipeline**
- Flow diagram: Commits → Patch Parsing → Import Detection → Classification
- Size: 1/2 page width

**Figure 2: PRs with New Libraries by Language**
- Bar chart: % PRs adding new libraries (Go: 0.2%, Python: 1.7%, TS: 3.2%)
- Size: 1/3 page width

**Table 2: Library Usage Statistics**
- Rows: Go, Python, TypeScript
- Columns: Total Libs, Stdlib, External, Avg per PR, % with Versions
- Size: 1/2 column width

**Figure 3: Version Operator Distribution**
- Stacked bar chart: Python (==, >=, ~=), TypeScript (^, ~, >=), Go (all versioned)
- Size: 1/2 page width

**Table 3: Top 10 Most Common New Libraries**
- 3 sub-tables (Go, Python, TypeScript)
- Columns: Library Name, Frequency
- Size: Full column width (compact)

---

## Additional Analysis Required

### High Priority (For RQ5 - Agent Comparison)

1. **Per-Agent Statistics** ✅ Data available in PR results
   - Break down RQ1-4 by agent (Claude Code, Cursor, Devin, Copilot, Codex)
   - Create comparison table or chart
   - Expected insight: Codex may be more conservative due to older training

2. **Agent-Specific Library Preferences**
   - Top 5 libraries per agent
   - Unique libraries per agent
   - Expected insight: Different agents may favor different libraries

### Medium Priority (For RQ6 - Invalid Libraries)

3. **Library Validation** ⚠️ Not yet implemented
   - Check against PyPI (Python), npm (JavaScript/TypeScript), Go packages (Go)
   - Identify non-existent or typo'd libraries
   - Estimate: ~8 hours implementation, 2 hours analysis
   - Expected finding: <1% invalid libraries (agents are trained on real code)

### Low Priority (If Time Permits)

4. **Temporal Trends**
   - Library usage over time (by PR creation date)
   - Agent evolution analysis
   - Estimate: ~4 hours analysis
   - Expected insight: Newer agents may adopt newer libraries

5. **Repository Context**
   - Do agents match existing project style?
   - Compare agent PRs to human PRs in same repos
   - Estimate: ~12 hours (requires human PR data)
   - Expected insight: Agents adapt to project conventions

---

## Writing Strategy

### Week 1: Initial Draft
- [ ] Day 1-2: Introduction + Dataset (leverage RESEARCH_PLAN.md)
- [ ] Day 3-4: Methodology (leverage existing code documentation)
- [ ] Day 5-7: Results sections (use aggregated_statistics.json)

### Week 2: Analysis + Refinement
- [ ] Day 1-2: Additional analysis (RQ5 agent comparison)
- [ ] Day 3-4: Create all figures and tables
- [ ] Day 5-6: Discussion + Ethical implications + Threats
- [ ] Day 7: Conclusion + References

### Week 3: Revision + Polishing
- [ ] Day 1-2: Internal review and feedback incorporation
- [ ] Day 3-4: Page limit compliance (strict 4+1 pages)
- [ ] Day 5-6: Anonymization and formatting
- [ ] Day 7: Final proofreading and submission prep

### Critical Success Factors
1. **Stay focused**: 4 RQs maximum, drop RQ5/RQ6 if space is tight
2. **Visualizations first**: Design figures before writing, structure around them
3. **Quantify everything**: Every claim needs a number
4. **Comparative insights**: Always compare across languages or agents
5. **Practical implications**: What should developers/tool builders do?

---

## Key Differentiators from Prior Work

### Compared to MSR 2024 Papers (DevGPT Challenge)
- **Scale**: 23,791 PRs vs typical 100-500 conversations
- **Scope**: 5 agents vs single agent (ChatGPT)
- **Focus**: Production code (merged PRs) vs chatbot interactions
- **Depth**: Language-specific patterns vs general insights

### Compared to "Library Versions" Paper (Raj & Costa, MSR 2024)
- **Context**: Merged PRs vs chat conversations
- **Agent diversity**: 5 agents vs ChatGPT only
- **Analysis depth**: Multi-language comparison vs single analysis
- **Contribution**: First study of agent library usage in real production code

### Novel Contributions
1. **First** large-scale analysis of library usage in agent-authored PRs
2. **First** cross-agent comparison of dependency management
3. **First** language-specific patterns in agent behavior
4. **Largest** dataset of agent-authored code analyzed (23,791 PRs)

---

## Backup Plan (If Page Limit Issues)

### Elements to Cut (Priority Order)
1. RQ5 (Agent comparison) - Move to "Future Work"
2. Figure 1 (Pipeline) - Replace with inline text description
3. Extensive related work - Trim to 2-3 sentences
4. Discussion subsections - Consolidate into bullet points
5. Detailed threats to validity - Keep to 3-4 sentences

### Elements to Keep (Must-Have)
1. RQ1-4 with quantitative results
2. Table 2 (Library statistics)
3. Figure 2 (PRs with new libraries)
4. Table 3 (Top libraries)
5. Ethical implications section (required)

---

## Success Criteria

### Paper Acceptance Indicators
- ✅ Novel dataset and research questions
- ✅ Rigorous methodology (reproducible)
- ✅ Clear quantitative findings
- ✅ Practical implications
- ✅ Proper anonymization and formatting

### Best Paper Award Considerations
- Open Science: ✅ Code and data publicly available
- Impact: Informs agent designers and developers
- Quality: Comprehensive analysis across 3 languages and 5 agents
- Novelty: First study of its kind

---

## References to Include

### Essential Citations (Must-Have)
1. AIDev dataset paper (Hao Li et al.)
2. MSR 2024 Library Versions paper (Raj & Costa)
3. DevGPT dataset paper (Xiao et al.)
4. Agent tools: Claude Code, Cursor, Devin, Copilot, Codex papers

### Supporting Citations (Nice-to-Have)
5. Dependency management practices (prior MSR work)
6. Software quality and dependencies (empirical SE)
7. Code generation and LLMs (FSE, ICSE papers)
8. Library recommendation systems

### Target: 15-20 references total

---

## Contact & Submission

- **Submission portal**: https://msr2026-challenge.hotcrp.com/
- **Abstract deadline**: December 18, 2025 (optional but encouraged)
- **Paper deadline**: December 23, 2025 (AoE, UTC-12h)
- **Notification**: January 15, 2026
- **Camera-ready**: January 23, 2026

---

*Last updated: November 20, 2025*
*Status: Analysis complete, ready for writing phase*
