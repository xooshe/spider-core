# spider-core

`spider-core` is a reusable Django/DRF helper library extracted from the Spiderkube admin project.
It provides:

- Django model mixins and base classes
- DRF API abstractions for CRUD and list views
- serializer helpers
- admin base classes
- reusable decorators and exceptions
- caching helpers
- secure storage helpers
- JSON serializer utilities
- field validators

## Installation

Install the package locally from the repository root:

```bash
pip install -e .
```

Install with optional admin helpers:

```bash
pip install -e .[admin]
```

Install with optional storage helpers:

```bash
pip install -e .[storage]
```

Install directly from GitHub:

```bash
pip install git+https://github.com/xooshe/spider-core.git
```

Install from PyPI:

```bash
pip install spider-core-x
```

Install with optional admin helpers from PyPI:

```bash
pip install spider-core-x[admin]
```

Install with optional storage helpers from PyPI:

```bash
pip install spider-core-x[storage]
```

## CI / Publishing

A GitHub Actions workflow is included at `.github/workflows/publish.yml`. It:

- runs unit tests on push and pull request
- builds the package on push and pull request
- publishes to PyPI when a `v*` tag is pushed

No secrets are needed—the workflow uses OIDC trusted publishing for PyPI authentication.

To publish a new version:

```bash
git tag v0.1.1
git push origin v0.1.1
```

The workflow will automatically build and publish `spider-core-x` to PyPI.

## Usage

```python
from spider.api import ModelGetApi
from spider.models import AbstractBaseModel
from spider.serializers import ModelSerializer
from spider.decorators import api_response
```

## Package structure

- `spider/api`
- `spider/admin`
- `spider/models`
- `spider/serializers`
- `spider/decorators`
- `spider/exeptions`
- `spider/storage`
- `spider/utils`
- `spider/validators`
