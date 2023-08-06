# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_table_sort']

package_data = \
{'': ['*'], 'django_table_sort': ['static/*']}

install_requires = \
['django>=3.0']

setup_kwargs = {
    'name': 'django-table-sort',
    'version': '0.2.11',
    'description': 'Create tables with sorting links on the headers in Django templates.',
    'long_description': '# Django-table-sort\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TheRealVizard/django-table-sort/main.svg)](https://results.pre-commit.ci/latest/github/TheRealVizard/django-table-sort/main) [![Documentation Status](https://readthedocs.org/projects/django-table-sort/badge/?version=latest)](https://django-table-sort.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/TheRealVizard/django-table-sort/branch/main/graph/badge.svg?token=KGXHPZ6HOB)](https://codecov.io/gh/TheRealVizard/django-table-sort) ![django-table-sort](https://img.shields.io/pypi/v/django-table-sort?color=blue) ![python-versions](https://img.shields.io/pypi/pyversions/django-table-sort) ![django-versions](https://img.shields.io/pypi/frameworkversions/django/django-table-sort?label=django) ![license](https://img.shields.io/pypi/l/django-table-sort?color=blue) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) ![downloads](https://img.shields.io/pypi/dm/django-table-sort)\n\nCreate tables with sorting links on the headers in Django templates.\n\nThis is currently [WIP](https://en.wikipedia.org/wiki/Work_in_process), so many other features will come in future releases.\n## Installation\n\n**First**, install with pip:\n\n```bash\npip install django-table-sort\n```\n\n**Second**, add the app to your INSTALLED_APPS setting:\n\n```python\nINSTALLED_APPS = [\n    ...,\n    "django_table_sort",\n    ...,\n]\n```\n\n## Usage\n**First**, add the static to your Template:\n\n```html\n<link rel="stylesheet" href="{% static \'django_table_sort.css\' %}"/>\n```\n\n`django-sort-table` uses by default Font Awesome 6 to display the icons, so you might need to add it too.\n\n```html\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.2/css/all.min.css" integrity="sha512-1sCRPdkRXhBV2PBLUdRb4tMg1w2YPf37qatUFeS7zlBy7jJI8Lf4VHwWfZZfpXtYSLy85pkm9GaYVYMfw5BC1A==" crossorigin="anonymous" referrerpolicy="no-referrer" />\n```\n\n**Second**, Use `django-table-sort` to display your tables.\n\nIn your _view.py_ file:\n\n```python\nclass ListViewExample(ListView):\n    model = Person\n    template_name: str = "base.html"\n    ordering_key = "o"\n\n    def get_ordering(self) -> tuple:\n        return self.request.GET.getlist(\n            self.ordering_key, None\n        )  # To make Django use the order\n\n    def get_context_data(self, **kwargs):\n        context = super().get_context_data(**kwargs)\n        context["table"] = TableSort(\n            self.request,\n            self.object_list,\n            sort_key_name=self.ordering_key,\n            table_css_clases="table table-light table-striped table-sm",\n        )\n        return context\n```\n\nIn your _template.html_ file:\n\n```html\n{{ table.render }}\n```\n\nResult:\n\nThe table is render with 2 link, one to Toggle the sort direction and another to remove the sort.\n\n<p align="center">\n    <img width="375" height="149" src=".\\result.png">\n</p>\n\nYou can filter by each field you declare as a column.\n<p align="center">\n    <img width="375" height="45" src=".\\url_result.png">\n</p>\n',
    'author': 'TheRealVizard',
    'author_email': 'vizard@divineslns.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheRealVizard/django-table-sort',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
