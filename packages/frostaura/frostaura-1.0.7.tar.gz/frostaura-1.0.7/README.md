# fa.intelligence.notebooks
## Description
FrostAura Intelligence provides a range of open-source notebooks for Python-based machine learning solutions like:
- Utilities
- Environments
- Labs
- Experiments

## Getting Started
### Local
- Python >= 3.7 required.
- [Setup your environment.](./environments/README.md)

To build the Python package locally, from the root of the project, run `python -m build` (Legacy way: `python setup.py sdist bdist_wheel`).
### PIP Installation
```
pip install -U --no-cache-dir frostaura
````
#### Example Usage (See [all the examples here](https://github.com/faGH/fa.intelligence.notebooks/tree/main/examples).)
```
from frostaura import (models,
                       data_access,
                       engines,
                       managers)

html_data_access = data_access.HtmlDataAccess()
engine = engines.FinvizAssetValuationEngine(html_data_access=html_data_access)

vars(engine.valuate(symbol='AAPL', company_name='Apple Inc.'))
```

## Credits
- [Jeff Heaton's GitHub](https://github.com/jeffheaton/t81_558_deep_learning/blob/master/)

## Contribute
In order to contribute, simply fork the repository, make changes and create a pull request.

## Support
If you enjoy FrostAura open-source content and would like to support us in continuous delivery, please consider a donation via a platform of your choice.

| Supported Platforms | Link |
| ------------------- | ---- |
| PayPal | [Donate via Paypal](https://www.paypal.com/donate/?hosted_button_id=SVEXJC9HFBJ72) |

For any queries, contact dean.martin@frostaura.net.
