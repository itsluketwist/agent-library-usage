# Research Project Python Repository Rules

This is a companion repository for a research project, therefore, all code should be simple and well-explained.

If this is the first time you encounter a new repository:
- Update any lines with an @claude comment (removing the comment afterwards).
- Set up a virtual environment if one doesn't exist. Environment should be Python3.12, and in the .venv directory.

Style notes:
- You should comprehensively use Python typings
- Class and method docstrings should be concise but well explained, do not include parameter information, if there is a return then the last sentence should be on a separate line and begin "Returns ..." with an explanation.
- Each non-empty file should have a short docstring on the first line.
- Reusable code should be stored in `src`, one-off code should be in Jupyter notebooks and stored in `notebooks`.
- Only use classes when it makes sense, it is not always necessary for every method in a file to be a part of the same class.
- Always have a trailing comma in method arguments on definition, or the parameters when calling. You should prefer tall code over wide code.
