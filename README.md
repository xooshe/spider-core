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

Install directly from GitHub once the repository exists:

```bash
pip install git+https://github.com/<owner>/<repo>.git
```

Install from a private Python Artifactory repository once published:

```bash
pip install --index-url https://<artifactory-host>/artifactory/api/pypi/<repo-name>/simple spider-core
```

## CI / Publishing

A GitHub Actions workflow is included at `.github/workflows/publish.yml`. It:

- builds the package on push and pull request
- publishes artifacts to Artifactory when a `v*` tag is pushed

Set these repository secrets before publishing:

- `ARTIFACTORY_USERNAME`
- `ARTIFACTORY_PASSWORD`
- `ARTIFACTORY_REPOSITORY_URL`

Create a release tag like:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Then the workflow will build and upload `spider-core` to your Artifactory repository.

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
