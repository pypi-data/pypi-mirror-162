# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nmdc_schema']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.3.0,<23.0.0',
 'click-log>=0.4.0,<0.5.0',
 'deepdiff>=5.8.0,<6.0.0',
 'linkml',
 'linkml-runtime',
 'openpyxl==3.0.7',
 'pandasql>=0.7.3,<0.8.0',
 'pandoc',
 'pymongo>=4.1.0,<5.0.0',
 'sqldf>=0.4.2,<0.5.0',
 'strsimpy>=0.2.1,<0.3.0']

entry_points = \
{'console_scripts': ['fetch-nmdc-schema = '
                     'nmdc_schema.nmdc_data:get_nmdc_jsonschema',
                     'nmdc-data = nmdc_schema.nmdc_data:cli',
                     'nmdc-version = nmdc_schema.nmdc_version:cli',
                     'validate-nmdc-json = nmdc_schema.validate_nmdc_json:cli']}

setup_kwargs = {
    'name': 'nmdc-schema',
    'version': '6.0.0',
    'description': 'Schema resources for the National Microbiome Data Collaborative (NMDC)',
    'long_description': '# National Microbiome Data Collaborative Schema\n\n[![PyPI - License](https://img.shields.io/pypi/l/nmdc-schema)](https://github.com/microbiomedata/nmdc-schema/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/commits)\n[![GitHub issues](https://img.shields.io/github/issues/microbiomedata/nmdc-schema?branch=master&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/issues)\n[![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/issues?q=is%3Aissue+is%3Aclosed)\n[![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/pulls)\n\n![Deploy Documentation](https://github.com/microbiomedata/nmdc-schema/workflows/Build%20and%20Deploy%20Static%20Mkdocs%20Documentation/badge.svg?branch=main)\n\nThis repository defines a [linkml](https://github.com/linkml/linkml) schema for managing metadata from the [National Microbiome Data Collaborative (NMDC)](https://microbiomedata.org/). The NMDC is a multi-organizational effort to integrate microbiome data across diverse areas in medicine, agriculture, bioenergy, and the environment. This integrated platform facilitates comprehensive discovery of and access to multidisciplinary microbiome data in order to unlock new possibilities with microbiome data science. \n\nTasks managed by the repository are:\n\n-   Generating the schema\n-   Converting the schema from it\'s native LinkML/YAML format into other artifacts\n    -   [JSON-Schema](jsonschema/nmdc.schema.json)\n-   Deploying the schema as a PyPI package\n-   Deploying the [documentation](https://microbiomedata.github.io/nmdc-schema/) \n\n## Background\n\nThe NMDC [Introduction to metadata and ontologies](https://microbiomedata.org/introduction-to-metadata-and-ontologies/) primer provides some the context for this project.\n\nSee also [these slides](https://microbiomedata.github.io/nmdc-schema/schema-slides.html) ![](images/16px-External.svg.png) describing the schema.\n\n## Dependencies\nIn order to make new release of the schema, you must have the following installed on your sytem:\n- [poetry](https://python-poetry.org/docs/#installation/)\n- [pandoc](https://pandoc.org/installing.html)\n\n## Maintaining the Schema\n\nSee [MAINTAINERS.md](MAINTAINERS.md) for instructions on maintaining and updating the schema.\n\n## NMDC metadata downloads\n\nSee https://github.com/microbiomedata/nmdc-runtime/#data-exports\n\n## Ecosystem Diagram\n\n```mermaid\nflowchart TD\n    subgraph nmdc-schema repo\n    ly([NMDC LinkML YAML files])\n    lg(generated artifacts)\n    ly-.make all.->lg\n    end\n    subgraph Data Validation\n    click ly href "https://github.com/microbiomedata/nmdc-schema/tree/main/src/schema" _top\n    d[(Some data)]\n    v[[Validation process]]\n    v--Has input-->d\n    v--Has input-->ly\n    end\n    subgraph MIxS\n    m([MIxS Schema])\n    end\n    subgraph SubmissionPortal\n    sppg[(Postgres)]\n    spa[Portal API]\n    sppg<-->spa\n    click spa href "https://data.dev.microbiomedata.org/docs" _top\n    ps[Pydantic schema]\n    end\n    subgraph MongoDB\n    mc[(Collections)]\n    ms[Implicit schema]\n    ma[Search API]\n    mc<-->ma\n    click ma href "https://api.dev.microbiomedata.org/docs" _top\n    end\n    mc --Ingest--> sppg\n    subgraph DH Template Prep\n    saf[sheets_and_friends repo]\n    sps([Submission Portal Schema])\n    dhjs[Data Harmoizer JS, etc.]\n    saf-->sps-->dhjs\n    end\n    dhjs-->SubmissionPortal\n    subgraph DataMapping\n    sa[sample-annotator repo]\n    end\n    spa-->sa-..->ma\n    ly-..->ps\n    sj[some json]\n    ly-..->sj-..->MongoDB-..->ps\n```\n',
    'author': 'Bill Duncan',
    'author_email': 'wdduncan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://microbiomedata.github.io/nmdc-schema/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
