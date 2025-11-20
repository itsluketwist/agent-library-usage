# MSR 2026 Mining Challenge Paper Write-Up Plan

## Paper Title (Draft)
**"Library Dependency Patterns in Agent-Authored Pull Requests: An Empirical Study of AIDev"**

Alternative titles:
- "How Conservative Are AI Coding Agents? An Analysis of Library Usage in Agent-Authored PRs"
- "External Library Adoption in AI-Generated Code: Evidence from 23,791 Pull Requests"

---

## Paper Requirements (Strict)
- **Length**: 4 pages + 1 page references (NO exceptions)
- **Format**: ACM sigconf (double-column)
- **Review**: Double-anonymous
- **Required sections**: Ethical implications before conclusion
- **Deadline**: December 23, 2025
- **Conference**: MSR 2026, April 27 - May 4, 2026, Trondheim, Norway

---

## Refined Research Questions

### Primary RQs (Core of Paper)

**RQ1: How frequently do AI coding agents add new external library dependencies?**
- **Motivation**: Understanding if agents are conservative or experimental with dependencies
- **Metrics**:
  - % PRs adding new libraries (0.2% Go, 1.7% Python, 3.2% TypeScript)
  - % PRs modifying dependency files (1.8% Go, 9.4% Python, 25.3% TypeScript)
  - Comparison across languages and agents
- **Insight**: Agents are surprisingly conservative, especially for compiled languages

**RQ2: Do AI agents prefer standard library imports over external dependencies?**
- **Motivation**: Assessing if agents follow best practices of minimizing dependencies
- **Metrics**:
  - Ratio of stdlib vs external imports (55:641 Go, 49:1250 Python, 25:2614 TypeScript)
  - Avg libraries per PR (0.97 Go, 2.13 Python, 2.63 TypeScript)
- **Insight**: Agents heavily favor stdlib but vary significantly by language ecosystem

**RQ3: How do AI agents specify library versions in dependency files?**
- **Motivation**: Version specification is critical for reproducibility and security
- **Metrics**:
  - % dependencies with version specs (100% Go/TypeScript, 84% Python)
  - Distribution of version operators (Python: `==` 670, TypeScript: `^` 1884)
- **Insight**: Agents are diligent about versions, with language-specific patterns

**RQ4: What are the most commonly adopted libraries by AI agents across languages?**
- **Motivation**: Understanding agent preferences and potential biases
- **Metrics**:
  - Top 10 libraries per language (with frequency)
  - Common patterns (e.g., openai, testing frameworks)
- **Insight**: Reveals agent training data influence and practical developer needs

### Optional Secondary RQs (If space permits)

**RQ5: How does library usage vary across different AI coding agents?**
- **Motivation**: Comparing agent behaviors (Claude Code, Cursor, Devin, Copilot, Codex)
- **Metrics**: Per-agent statistics (requires additional analysis)
- **Note**: OpenAI Codex dominates dataset (16,487/23,802 PRs), may skew results

**RQ6: Do agents introduce invalid or non-existent library dependencies?**
- **Motivation**: Quality and reliability concerns
- **Metrics**: Validation against PyPI, npm, Go packages (requires additional analysis)
- **Note**: Mentioned in RESEARCH_PLAN.md but not yet implemented

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

### Page 3: Results Part 1 (~1.0 page)

**3.1 RQ1: Frequency of New Dependencies (0.35 page)**
- **Finding**: Agents are highly conservative
  - Go: 0.2% PRs add new libraries (16/10,107)
  - Python: 1.7% (122/7,190)
  - TypeScript: 3.2% (207/6,494)
- **Dependency file changes** are more common (1.8-25.3%)
- **Interpretation**: Agents modify existing dependencies more than adding new ones
- **Figure 2**: Bar chart comparing % PRs with new libs across languages

**3.2 RQ2: Standard Library vs External (0.35 page)**
- **Finding**: Heavy stdlib preference, but varies by ecosystem
  - Go: 55 stdlib, 641 external (8:92 ratio)
  - Python: 49 stdlib, 1,250 external (4:96 ratio)
  - TypeScript: 25 stdlib, 2,614 external (1:99 ratio)
- **Average libraries per PR**: 0.97 (Go), 2.13 (Python), 2.63 (TypeScript)
- **Interpretation**: Language ecosystem maturity affects agent behavior
- **Table 2**: Library counts and ratios per language

**3.3 RQ3: Version Specifications (0.3 page)**
- **Finding**: Agents are diligent with versions
  - Go/TypeScript: 100% specify versions
  - Python: 83.9% (759/905)
- **Version operators**:
  - Python prefers exact versions (`==`: 670)
  - TypeScript prefers compatible ranges (`^`: 1,884)
  - Go uses module versions (all versioned)
- **Figure 3**: Version operator distribution (stacked bar chart)

### Page 4: Results Part 2 + Discussion + Conclusion (~1.0 page)

**3.4 RQ4: Most Common Libraries (0.25 page)**
- **Top libraries per language** (Table 3):
  - Python: openai (18), requests (17), numpy (15), pandas (13)
  - TypeScript: typescript (123), @types/node (84), eslint (52), zod (48)
  - Go: snappy (6), testify (3), yaml.v3 (3)
- **Patterns**: Testing frameworks, type systems, AI/ML libraries
- **Interpretation**: Reflects agent training data and practical developer needs

**4. Discussion (0.3 page)**
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
