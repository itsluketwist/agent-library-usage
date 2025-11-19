# Research Plan: Library Usage by AI Coding Agents

## MSR 2026 Mining Challenge Submission

### Research Questions

1. **Library Adoption**: Do agents happily import and install new libraries?
2. **Existing Dependencies**: Do agents willingly use external libraries that are already installed, or do they avoid them?
3. **Invalid Libraries**: Do agents try to commit invalid or non-existent libraries?
4. **Version Specifications**: Do agents specify library versions in their PRs?
5. **Common Libraries**: What are the most frequently used libraries by agents across different programming languages?

---

## Implementation Status

### ✅ Completed

1. **Dataset Setup**
   - Created notebook to download AIDev dataset from Hugging Face
   - Dataset contains 33,596 agent-authored PRs from 2,807 repositories
   - 5 AI agents: Claude Code, Cursor, Devin, GitHub Copilot, OpenAI Codex

2. **Library Extraction Module** (`src/library_extractor.py`)
   - Python import extraction (from/import statements)
   - JavaScript/TypeScript import extraction (import/require)
   - Package manager file parsing:
     - Python: requirements.txt, setup.py, pyproject.toml
     - JavaScript/TypeScript: package.json
     - Go: go.mod
     - Rust: Cargo.toml
   - Version specification detection
   - Standard library vs external library classification

3. **PR Analysis Module** (`src/pr_analyzer.py`)
   - Analyzes commit details for library usage patterns
   - Tracks:
     - Libraries imported in code files
     - Libraries added to dependency files
     - New vs existing library usage
     - Version specifications
     - Dependency file changes (added/modified)
   - Aggregates statistics across PRs

4. **Analysis Notebooks**
   - `01_download_dataset.ipynb`: Download and cache AIDev dataset
   - `02_explore_languages.ipynb`: Identify top 3 programming languages
   - `03_analyze_library_usage.ipynb`: Main analysis and visualizations

---

## Next Steps

### Phase 1: Data Collection (Immediate)

1. **Run the dataset download notebook**
   ```bash
   jupyter notebook notebooks/01_download_dataset.ipynb
   ```
   This will download ~5-10 GB of data to the `data/` directory.

2. **Explore language distribution**
   ```bash
   jupyter notebook notebooks/02_explore_languages.ipynb
   ```
   This will identify the top 3 languages (expected: TypeScript, Python, JavaScript).

### Phase 2: Analysis (1-2 days)

3. **Run the main analysis**
   ```bash
   jupyter notebook notebooks/03_analyze_library_usage.ipynb
   ```
   This will:
   - Extract library usage from all PRs in top 3 languages
   - Generate statistics and visualizations
   - Save results to `output/` directory

### Phase 3: Additional Analysis (2-3 days)

4. **Enhance analysis with additional insights**:

   **a) Invalid Library Detection**
   - Check if imported libraries exist in package indexes (PyPI, npm)
   - Detect typos in library names (e.g., "requets" vs "requests")
   - Compare against a list of known libraries

   **b) Agent Comparison**
   - Compare library usage patterns across different agents
   - Do some agents prefer certain libraries over others?
   - Which agents are more likely to add new dependencies?

   **c) Temporal Analysis**
   - How has library usage changed over time?
   - Are newer PRs more likely to use external libraries?

   **d) Repository Context**
   - Analyze existing dependencies in repositories
   - Do agents reuse existing dependencies or add new ones?
   - Correlate with repository size, stars, language

### Phase 4: Paper Writing (3-5 days)

5. **Key findings to report**:
   - Percentage of PRs that add new libraries
   - Percentage of PRs that specify versions
   - Most common version operators (==, >=, ~, ^)
   - Most popular libraries by language and agent
   - Comparison of standard library vs external library usage
   - Invalid library detection results
   - Agent-specific patterns and preferences

6. **Visualizations to create**:
   - Library usage distribution across languages
   - Version specification patterns
   - Top 20 most common libraries per language
   - Agent comparison charts
   - Temporal trends
   - External vs stdlib ratio

---

## Data Files

### Downloaded (from Hugging Face)
- `data/all_repository.parquet` - All repository metadata
- `data/all_pull_request.parquet` - All pull request metadata
- `data/all_user.parquet` - User information
- `data/repository.parquet` - Popular repositories (100+ stars)
- `data/pull_request.parquet` - PRs from popular repositories
- `data/pr_commit_details.parquet` - File-level changes with diffs

### Generated (analysis results)
- `output/{language}_library_usage.json` - Detailed per-PR results
- `output/aggregated_statistics.json` - Summary statistics
- `output/library_usage_comparison.png` - Visualization

---

## Code Structure

```
src/
├── library_extractor.py   # Extract imports/dependencies from code
├── pr_analyzer.py         # Analyze PRs for library usage
├── cli.py                 # Command-line interface (placeholder)
└── main.py                # Main entry point (placeholder)

notebooks/
├── 01_download_dataset.ipynb        # Download AIDev dataset
├── 02_explore_languages.ipynb       # Language exploration
└── 03_analyze_library_usage.ipynb   # Main analysis

data/                      # Downloaded datasets (gitignored)
output/                    # Analysis results (gitignored)
```

---

## Additional Analysis Ideas

### 1. Library Validation
- Use PyPI/npm APIs to check if libraries exist
- Detect common typos (Levenshtein distance)
- Check for deprecated libraries

### 2. Dependency Complexity
- Count total dependencies added per PR
- Analyze dependency chains (direct vs transitive)
- Security vulnerability detection

### 3. Code Quality Metrics
- Correlation between library usage and PR review time
- Correlation with PR acceptance/rejection
- Unused imports detection

### 4. Domain Analysis
- Cluster repositories by domain (web, ML, CLI tools, etc.)
- Library preferences by domain
- Agent specialization by domain

### 5. Human-Agent Collaboration
- Do PRs with agent contributions differ from human-only PRs?
- Review comments about library choices
- Library changes in review process

---

## Expected Contributions

This paper will provide the first large-scale empirical study of how AI coding agents handle external library dependencies, offering insights into:

1. **Agent Behavior**: Quantitative understanding of how agents use libraries
2. **Best Practices**: Patterns that could inform agent development
3. **Risk Assessment**: Identification of potential issues (invalid libs, version conflicts)
4. **Tool Development**: Foundation for tools to improve agent library usage
5. **Future Research**: Baseline for comparing future agent capabilities

---

## Timeline

- **Week 1**: Data download and exploration ✅ (Done!)
- **Week 2**: Main analysis and statistics generation
- **Week 3**: Enhanced analysis and agent comparison
- **Week 4**: Paper writing and visualizations
- **Week 5**: Review, refinement, and submission

---

## Questions to Answer in the Paper

1. How frequently do agents add new library dependencies? (RQ1)
2. Do agents prefer standard libraries or external packages? (RQ2)
3. What percentage of agent-added libraries are invalid? (RQ3)
4. How often do agents specify version constraints? (RQ4)
5. What are the most common libraries across languages? (RQ5)
6. Do different agents exhibit different library usage patterns?
7. How does library usage correlate with PR acceptance?
8. What patterns can inform better agent development?

---

## References

- AIDev Dataset: https://huggingface.co/datasets/hao-li/AIDev
- MSR 2026 Mining Challenge: https://2026.msrconf.org/track/msr-2026-mining-challenge
- Research Paper: "The Rise of AI Teammates in Software Engineering (SE) 3.0" (arXiv:2507.15003)
