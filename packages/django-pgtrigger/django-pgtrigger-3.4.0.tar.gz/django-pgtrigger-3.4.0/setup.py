# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgtrigger',
 'pgtrigger.management',
 'pgtrigger.management.commands',
 'pgtrigger.tests',
 'pgtrigger.tests.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-pgtrigger',
    'version': '3.4.0',
    'description': 'Postgres trigger support integrated with Django models.',
    'long_description': 'django-pgtrigger\n################\n\n``django-pgtrigger`` helps you write\n`Postgres triggers <https://www.postgresql.org/docs/current/sql-createtrigger.html>`__\nfor your Django models. It is compatible with Python 3.7 to 3.10 and Django 2.2 to 4.1.\n\nWhy should I use triggers?\n==========================\n\nTriggers can solve a variety of complex problems much more reliably and succinctly than application code. For example,\n\n1. Protecting operations on rows or columns (``pgtrigger.Protect``).\n2. Soft-deleting models (``pgtrigger.SoftDelete``).\n3. Snapshotting and tracking model changes (`django-pghistory <https://django-pghistory.readthedocs.io/>`__).\n4. Enforcing field transitions (``pgtrigger.FSM``).\n5. Keeping a search vector updated for full-text search (``pgtrigger.UpdateSearchVector``).\n6. Building official interfaces\n   (e.g. enforcing use of ``User.objects.create_user`` and not\n   ``User.objects.create``).\n7. Versioning models, mirroring fields, computing unique model hashes, and the list goes on...\n\nAll of these examples require no overridden methods, no base models, and no signal handling.\n\nQuick start\n===========\n\nInstall ``django-pgtrigger`` with ``pip3 install django-pgtrigger`` and\nadd ``pgtrigger`` to ``settings.INSTALLED_APPS``.\n\n``pgtrigger.Trigger`` objects are added to ``triggers`` in model\n``Meta``. ``django-pgtrigger`` comes with several trigger classes,\nsuch as ``pgtrigger.Protect``. In the following, we\'re protecting\nthe model from being deleted:\n\n.. code-block:: python\n\n    class ProtectedModel(models.Model):\n        """This model cannot be deleted!"""\n\n        class Meta:\n            triggers = [\n                pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)\n            ]\n\nWhen migrations are created and executed, ``ProtectedModel`` will raise an internal\ndatabase error anytime someone tries to delete it.\n\nLet\'s extend this example further and only protect deletions on inactive objects.\nIn this example, the trigger conditionally runs when the row being deleted\n(the ``OLD`` row in trigger terminology) is still active:\n\n.. code-block:: python\n\n    class ProtectedModel(models.Model):\n        """Active object cannot be deleted!"""\n        is_active = models.BooleanField(default=True)\n\n        class Meta:\n            triggers = [\n                pgtrigger.Protect(\n                    name="protect_deletes",\n                    operation=pgtrigger.Delete,\n                    condition=pgtrigger.Q(old__is_active=True)\n                )\n            ]\n\n\n``django-pgtrigger`` uses ``pgtrigger.Q`` and ``pgtrigger.F`` objects to\nconditionally execute triggers based on the ``OLD`` and ``NEW`` rows.\nCombining these Django idioms with ``pgtrigger.Trigger`` objects\ncan solve a wide variety of problems without ever writing SQL. Users,\nhowever, can still use raw SQL for complex cases.\n\nTriggers are installed like other database objects. Run\n``python manage.py makemigrations`` and ``python manage.py migrate`` to install triggers.\n\nIf triggers are new to you, don\'t fret.\nThe `pgtrigger docs <https://django-pgtrigger.readthedocs.io/>`__ break\ndown the core components of a trigger in the tutorial. They also\nprovide many more examples.\n\nDocumentation\n=============\n\n`View the pgtrigger docs here <https://django-pgtrigger.readthedocs.io/>`__\n\nOther Material\n==============\n\nAfter you\'ve read the docs, check out\n`this tutorial <https://wesleykendall.github.io/django-pgtrigger-tutorial/>`__\nwith interactive examples from a Django meetup talk.\n\nThe `DjangoCon 2021 talk <https://www.youtube.com/watch?v=Tte3d4JjxCk>`__\nalso breaks down triggers and shows several examples.\n\nInstallation\n============\n\nInstall django-pgtrigger with::\n\n    pip3 install django-pgtrigger\n\nAfter this, add ``pgtrigger`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-pgtrigger for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall, wesleykendall@protonmail.com)\n\nOther Contributors\n==================\n\n- @jzmiller1\n- @rrauenza\n- @ralokt\n',
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgtrigger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
