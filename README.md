# **research-template**

This repository contains the artifacts and full results for the research paper **...**.

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

## *abstract*

todo

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

After [*installation*](#installation), all analysis is run through Jupyter notebooks in the [`notebooks/`](notebooks/) directory. Run the notebooks in order:

1. **`01_download_dataset.ipynb`** - Download and prepare the AIDev dataset
2. **`02_explore_languages.ipynb`** - Identify programming languages in the dataset
3. **`03_analyze_library_usage.ipynb`** - Analyse library usage patterns across all languages
4. **`04_generate_latex_tables.ipynb`** - Generate LaTeX tables for the research paper

Each notebook is self-contained and documents its purpose and outputs.

## *structure*

- [`data/`](data/) - Downloaded AIDev dataset files (parquet format, git-ignored)
- [`output/`](output/) - Generated analysis results:
  - `*_library_usage.json` - Per-language library usage data
  - `aggregated_statistics.json` - Summary statistics across all languages
  - `latex_tables.tex` - Generated LaTeX tables for the paper
- [`src/`](src/) - Main project code:
  - [`extractors/`](src/extractors/) - Language-specific library extractors:
    - `base.py` - Base extractor interface
    - `python.py` - Python import and requirements.txt extraction
    - `javascript.py` - JavaScript/TypeScript import and package.json extraction
    - `go.py` - Go import and go.mod extraction
    - `csharp.py` - C# using statements and .csproj extraction
    - `rust.py` - Rust use statements and Cargo.toml extraction
  - `pr_analyzer.py` - Analyse PRs for library usage patterns
  - `constants.py` - Shared constants and configurations
  - `main.py` - Main analysis entry point
- [`notebooks/`](notebooks/) - Jupyter notebooks for the analysis pipeline:
  - `01_download_dataset.ipynb` - Download and prepare the AIDev dataset
  - `02_explore_languages.ipynb` - Identify programming languages in the dataset
  - `03_analyze_library_usage.ipynb` - Analyse library usage patterns (generates output/*.json)
  - `04_generate_latex_tables.ipynb` - Generate LaTeX tables for the paper (4 languages: TypeScript, Python, Go, C#)
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
