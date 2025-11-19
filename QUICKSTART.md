# Quick Start Guide

## Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd agent-library-usage
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install .
   ```

## Running the Analysis

### Step 1: Download the Dataset

Open and run the first notebook:
```bash
jupyter notebook notebooks/01_download_dataset.ipynb
```

This will download the AIDev dataset from Hugging Face. Files will be saved to the `data/` directory.

**Expected output:**
- `data/all_repository.parquet` (repository metadata)
- `data/all_pull_request.parquet` (all PRs)
- `data/repository.parquet` (popular repos, 100+ stars)
- `data/pull_request.parquet` (PRs from popular repos)
- `data/pr_commit_details.parquet` (file changes and diffs)

**Time:** ~10-20 minutes (depending on internet speed)
**Size:** ~5-10 GB total

### Step 2: Explore Languages

Open and run the second notebook:
```bash
jupyter notebook notebooks/02_explore_languages.ipynb
```

This identifies the top 3 most popular programming languages in the dataset.

**Expected output:**
- Language distribution statistics
- Bar charts showing top languages
- `data/top3_languages_prs.parquet` (filtered dataset)

**Time:** ~2-5 minutes

### Step 3: Analyze Library Usage

Open and run the main analysis notebook:
```bash
jupyter notebook notebooks/03_analyze_library_usage.ipynb
```

This performs the core analysis of library usage patterns.

**Expected output:**
- Detailed library usage statistics per language
- Visualizations comparing languages
- `output/{language}_library_usage.json` (detailed results)
- `output/aggregated_statistics.json` (summary statistics)
- `output/library_usage_comparison.png` (visualization)

**Time:** ~30-60 minutes (depending on dataset size)

## Understanding the Results

### JSON Output Files

**`{language}_library_usage.json`** - Contains per-PR analysis:
```json
[
  {
    "pr_id": 12345,
    "repository_id": 67890,
    "language": "Python",
    "agent": "Claude Code",
    "libraries_in_code": ["requests", "pandas", "numpy"],
    "libraries_in_deps": ["requests==2.28.0", "pandas>=1.5.0"],
    "new_libraries": ["requests", "pandas"],
    "stdlib_imports": ["os", "sys"],
    "external_libs": ["requests", "pandas", "numpy"],
    "libs_with_version": 2,
    "libs_without_version": 1,
    "version_operators": {"==": 1, ">=": 1}
  }
]
```

**`aggregated_statistics.json`** - Summary statistics:
```json
{
  "Python": {
    "total_prs": 5000,
    "prs_with_new_libs": 2500,
    "pct_prs_with_new_libs": 50.0,
    "avg_libs_per_pr": 3.5,
    "total_unique_libs": 500,
    "most_common_libs": [["requests", 1200], ["pandas", 800], ...]
  }
}
```

### Key Metrics

1. **prs_with_new_libs** - Number of PRs that add new dependencies
2. **pct_prs_with_new_libs** - Percentage of PRs adding dependencies
3. **avg_libs_per_pr** - Average number of libraries imported per PR
4. **total_unique_libs** - Total unique libraries used
5. **pct_libs_with_version** - Percentage of deps with version specs
6. **most_common_libs** - Top 20 most frequently used libraries

## Next Steps

### Additional Analysis

See `RESEARCH_PLAN.md` for ideas on:
- Invalid library detection
- Agent comparison
- Temporal trends
- Repository context analysis

### Paper Writing

Use the generated statistics and visualizations to answer the research questions:
1. Do agents happily import new libraries?
2. Do they use existing libraries or avoid dependencies?
3. Do they commit invalid libraries?
4. Do they specify versions?
5. What are the most common libraries?

## Troubleshooting

### Out of Memory

If you run out of memory:
- Process one language at a time
- Use a smaller sample of the dataset
- Increase swap space

### Download Fails

If dataset download fails:
- Check internet connection
- Try downloading directly from Hugging Face
- Use the alternative download from Zenodo

### Import Errors

If you get import errors:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install --upgrade .`
- Check Python version: `python --version` (should be 3.11+)

## Tips

1. **Save intermediate results**: The notebooks save processed data to avoid recomputation
2. **Use sample data first**: Test on a small subset before running full analysis
3. **Monitor resources**: Keep an eye on RAM and disk space
4. **Parallel processing**: Consider using multiprocessing for large datasets

## Support

For questions or issues:
- Check `RESEARCH_PLAN.md` for detailed methodology
- Review notebook comments for explanations
- Examine source code in `src/` for implementation details
