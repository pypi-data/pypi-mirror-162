====================
pytest-json-fixtures
====================

.. image:: https://img.shields.io/pypi/v/pytest-json-fixtures.svg
    :target: https://pypi.org/project/pytest-json-fixtures
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-json-fixtures.svg
    :target: https://pypi.org/project/pytest-json-fixtures
    :alt: Python versions

JSON output for the ``--fixtures`` flag

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

This plugin takes the output generated when running ``pytest`` with the ``--fixtures`` flag, convert it into JSON format and stream it into a file.


Requirements
------------

You must have Python, pip and pytest to use this plugin.


Installation
------------

You can install "pytest-json-fixtures" via `pip`_ from `PyPI`_::

    $ pip install pytest-json-fixtures


Usage
-----

Run the command below::

    $ pytest --json-fixtures

The same result you would get with ``pytest --fixtures`` will be output in JSON in a ``fixtures.json`` file, the default file name.

If you want the output on a different file, just add it after the flag::

    $ pytest --json-fixtures output.json

Contributing
------------
Contributions are very welcome.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-json-fixtures" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/marcosanchotene/pytest-json-fixtures/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
