# **research-template**

<div>
    <!-- badges from : https://shields.io/ -->
    <!-- logos available : https://simpleicons.org/ -->
    <a href="https://creativecommons.org/licenses/by-sa/4.0/">
        <img alt="CC-BY-SA-4.0 License" src="https://img.shields.io/badge/Licence-CC_BY_SA_4.0-yellow?style=for-the-badge&logo=docs&logoColor=white" />
    </a>
    <a href="https://www.python.org/">
        <img alt="Python 3" src="https://img.shields.io/badge/Python_3-blue?style=for-the-badge&logo=python&logoColor=white" />
    </a>
</div>

## *about*

This repository contains the research code and analysis for investigating how AI coding agents use external libraries in the code they write. This work is being prepared for submission to the MSR 2026 Mining Challenge.

### Research Questions

1. **Library Adoption**: Do agents happily import and install new libraries?
2. **Existing Dependencies**: Do agents willingly use external libraries that are already installed, or do they avoid them?
3. **Invalid Libraries**: Do agents try to commit invalid or non-existent libraries?
4. **Version Specifications**: Do agents specify library versions in their PRs?
5. **Common Libraries**: What are the most frequently used libraries by agents across different programming languages?

### Dataset

We analyze the [AIDev dataset](https://huggingface.co/datasets/hao-li/AIDev) from the MSR 2026 Mining Challenge, which contains:
- 33,596 curated agent-authored pull requests (Agentic-PRs)
- Data from 2,807 popular GitHub repositories (100+ stars)
- Contributions from 5 AI agents: Claude Code, Cursor, Devin, GitHub Copilot, OpenAI Codex
- PR metadata, commits, comments, reviews, and file-level changes

### Methodology

Our analysis focuses on the **top 3 most popular programming languages** in the dataset (TypeScript, Python, JavaScript) and examines:

- Library imports in code files
- Package manager file changes (package.json, requirements.txt, etc.)
- Version specification patterns
- Comparison of standard library vs external library usage
- New dependencies added vs existing dependencies used

## *installation*

The code requires Python 3.11 or later to run.
Ensure you have it installed with the command below, otherwise download and install it from
[here](https://www.python.org/downloads/).

```shell
python --version
```

Now clone the repository code:

```shell
git clone **redacted**
```

Once cloned, install the requirements locally in a virtual environment:

```shell
python -m venv .venv

. .venv/bin/activate

pip install .
```

## *usage*

After [*installation*](#installation), there are 2 ways to run the experiment code.
The easiest of which is via the the [`main.ipynb`](main.ipynb) notebook, which fully describes
each experiment and provides the methods to run them.

You can also use the `run` command from your terminal - this is likely best if you want to
reproduce the experiments on an external server or in a [docker](https://www.docker.com/)
container.

```shell
run --dataset-file data/example.json
```

All other non-experiment code that likely only needed to be ran a single time is explained in,
and can be interfaced with, via it's corresponding Jupyter notebook.
These notebooks are contained in the [`notebooks/`](notebooks/) directory, and are described in the
[*structure*](#structure) section.

## *structure*

- [`data/`](data/) - Downloaded AIDev dataset files (parquet format)
- [`output/`](output/) - Generated analysis results, statistics, and visualizations
- [`src/`](src/) - Main project code:
  - `library_extractor.py` - Extract library imports from code files
  - `pr_analyzer.py` - Analyze PRs for library usage patterns
  - `cli.py` - Command-line interface
- [`notebooks/`](notebooks/) - Jupyter notebooks for analysis:
  - `01_download_dataset.ipynb` - Download the AIDev dataset
  - `02_explore_languages.ipynb` - Identify top programming languages
  - `03_analyze_library_usage.ipynb` - Main analysis and visualizations

## *development*

We use a few extra processes to ensure the code maintains a high quality.
First clone the project and create a virtual environment - as described above.
Now install the editable version of the project, with the development dependencies.

```shell
pip install --editable ".[dev]"
```

### *tests*

This project includes unit tests to ensure correct functionality.
Use [`pytest`](https://docs.pytest.org/en/stable/) to run the tests with:

```shell
pytest tests
```

### *linting*

We use [`pre-commit`](https://pre-commit.com/) to lint the code, run it using:

```shell
pre-commit run --all-files
```

### *dependencies*

We use [`uv`](https://astral.sh/blog/uv) for dependency management.
First add new dependencies to `requirements.in`.
Then version lock with [`uv`](https://astral.sh/blog/uv) using:

```shell
uv pip compile requirements.in --output-file requirements.txt --upgrade
```

## *paper*

todo

## *citation*

todo
