# **agent-library-usage**

This repository contains the artifacts and full results for the research paper **A Study of Library Usage in Agent-Authored Pull Requests**, accepted at the *23rd International Conference on Mining Software Repositories (MSR '26), April 13--14, 2026, Rio de Janeiro, Brazil*, and available on [arXiv](https://arxiv.org/abs/2512.11589).

<div>
    <!-- badges from : https://shields.io/ -->
    <!-- logos available : https://simpleicons.org/ -->
    <a href="https://creativecommons.org/licenses/by/4.0/">
        <img alt="CC-BY-4.0 License" src="https://img.shields.io/badge/Licence-CC_BY_4.0-yellow?style=for-the-badge&logo=docs&logoColor=white" />
    </a>
    <a href="https://www.python.org/">
        <img alt="Python 3" src="https://img.shields.io/badge/Python_3-blue?style=for-the-badge&logo=python&logoColor=white" />
    </a>
    <a href="https://code.claude.com/docs/en/overview">
        <img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-D97757?style=for-the-badge&logo=claude&logoColor=white" />
    </a>
    <a href="https://arxiv.org/abs/2512.11589">
        <img alt="arXiv" src="https://img.shields.io/badge/arXiv-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white" />
    </a>
</div>

## *abstract*

Coding agents are becoming increasingly capable of completing end-to-end software engineering workflows that previously required a human developer, including raising pull requests (PRs) to propose their changes.
However, we still know little about how these agents use libraries when generating code, a core part of real-world software development.
To fill this gap, we study 26,760 agent-authored PRs from the [AIDev dataset](https://huggingface.co/datasets/hao-li/AIDev) to examine three questions: how often do agents import libraries, how often do they introduce new dependencies (and with what versioning), and which specific libraries do they choose?
We find that agents often import libraries (29.5\% of PRs) but rarely add new dependencies (1.3\% of PRs); and when they do, they follow strong versioning practices (75.0\% specify a version), an improvement on direct LLM usage where versions are rarely mentioned.
Generally, agents draw from a surprisingly diverse set of external libraries, contrasting with the limited ``library preferences'' seen in prior non-agentic LLM studies.
Our results offer an early empirical view into how AI coding agents interact with today’s software ecosystems.

## *dataset*

This work is part of the [MSR 2026 Mining Challenge](https://2026.msrconf.org/track/msr-2026-mining-challenge), analysing the [AIDev dataset](https://huggingface.co/datasets/hao-li/AIDev), the first large-scale, openly available dataset of agent-authored pull requests from real-world GitHub repositories.
The dataset was introduced by [Li et al.](https://arxiv.org/abs/2507.15003) and captures the emergence of autonomous coding agents in software engineering, providing a unique opportunity to study how AI teammates interact with real-world codebases and software ecosystems.

**Dataset Version:** This research utilises [AIDev dataset](https://huggingface.co/datasets/hao-li/AIDev) revision [`eee0408a277826d88fc0ca5fa07d2fc325c96af1`](https://huggingface.co/datasets/hao-li/AIDev/commit/eee0408a277826d88fc0ca5fa07d2fc325c96af1) (November 2025 snapshot).

## *installation*

The code requires Python 3.11 or later to run.
Ensure you have it installed with the command below, otherwise download and install it from
[here](https://www.python.org/downloads/).

```shell
python --version
```

Now clone the repository code:

```shell
git clone https://github.com/itsluketwist/agent-library-usage
```

Once cloned, install the requirements locally in a virtual environment:

```shell
python -m venv .venv

. .venv/bin/activate

pip install .
```

## *usage*

After [*installation*](#installation), all analysis is run through Jupyter notebooks in the [`notebooks/`](notebooks/) directory. Run the notebooks in order:

1. **`01_download_dataset.ipynb`** - Download and prepare the [AIDev dataset](https://huggingface.co/datasets/hao-li/AIDev)
2. **`02_explore_languages.ipynb`** - Identify programming languages in the dataset
3. **`03_analyze_library_usage.ipynb`** - Analyse library usage patterns across all languages
4. **`04_generate_latex_tables.ipynb`** - Generate LaTeX tables for the research paper

Each notebook is self-contained and documents its purpose and outputs.

## *structure*

- [`data/`](data/) - Downloaded AIDev dataset files (parquet format, git-ignored)
- [`output/`](output/) - Generated analysis results:
  - `*_library_usage.json` - Per-language library usage data
  - [`aggregated_statistics.json`](output/aggregated_statistics.json) - Summary statistics across all languages
  - [`latex_tables.tex`](output/latex_tables.tex) - Generated LaTeX tables for the paper
- [`src/`](src/) - Main project code:
  - [`extractors/`](src/extractors/) - Language-specific library extractors:
    - [`base.py`](src/extractors/base.py) - Base extractor interface
    - [`python.py`](src/extractors/python.py) - Python import and requirements.txt extraction
    - [`javascript.py`](src/extractors/javascript.py) - JavaScript/TypeScript import and package.json extraction
    - [`go.py`](src/extractors/go.py) - Go import and go.mod extraction
    - [`csharp.py`](src/extractors/csharp.py) - C# using statements and .csproj extraction
    - [`rust.py`](src/extractors/rust.py) - Rust use statements and Cargo.toml extraction
  - [`pr_analyzer.py`](src/pr_analyzer.py) - Analyse PRs for library usage patterns
  - [`constants.py`](src/constants.py) - Shared constants and configurations
  - [`main.py`](src/main.py) - Main analysis entry point
- [`notebooks/`](notebooks/) - Jupyter notebooks for the analysis pipeline:
  - [`01_download_dataset.ipynb`](notebooks/01_download_dataset.ipynb) - Download and prepare the AIDev dataset
  - [`02_explore_languages.ipynb`](notebooks/02_explore_languages.ipynb) - Identify programming languages in the dataset
  - [`03_analyze_library_usage.ipynb`](notebooks/03_analyze_library_usage.ipynb) - Analyse library usage patterns (generates output/*.json)
  - [`04_generate_latex_tables.ipynb`](notebooks/04_generate_latex_tables.ipynb) - Generate LaTeX tables for the paper (4 languages: TypeScript, Python, Go, C#)
- [`tests/`](tests/) - Unit tests for extractors and analyser

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

## *citation*

If you use this work in your research, please cite our paper:

**ACM Reference Format:**

```
Lukas Twist and Jie M. Zhang. 2026. A Study of Library Usage in Agent-Authored Pull Requests. In 23rd International Conference on Mining Software Repositories (MSR '26), April 13–14, 2026, Rio de Janeiro, Brazil. ACM, New York, NY, USA, 6 pages. https://doi.org/10.1145/3793302.3793562
```

**BibTeX:**

```
@inproceedings{twist2026AgentLibraryUsage,
  title = {{A Study of Library Usage in Agent-Authored Pull Requests}},
  author = {Twist, Lukas and Zhang, Jie M.},
  booktitle = {Proceedings of the 23rd International Conference on Mining Software Repositories},
  series = {MSR '26},
  location = {Rio de Janeiro, Brazil},
  year = {2026},
  month = {April},
  publisher = {ACM},
  doi = {10.1145/3793302.3793562},
}
```

## *acknowledgments*

In a fitting twist of irony, this repository&ndash;which analyses how AI coding agents use libraries&ndash;was itself developed with assistance from [Claude Code](https://code.claude.com/docs/en/overview), an AI coding agent.
All code was thoroughly reviewed and validated by the authors, who remain responsible for the scientific interpretations and conclusions.
