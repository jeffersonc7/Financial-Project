# Financial-Project
An end-to-end data science project focused on processing, integrating, and analyzing financial statement data to build a structured panel dataset for statistical and machine learning analysis.

## Notebook setup

From the project root, install the project into the Python environment used by
your Jupyter kernel:

```bash
python -m pip install -e .
```

After that, notebooks can import project modules directly, for example:

```python
from src.azure_storage import get_filesystem
```

Repeat the install if you switch to a different virtual environment or Jupyter
kernel. The editable install means changes to files in `src/` are available
without reinstalling.