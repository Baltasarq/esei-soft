=================
 Flask-CeleryExt
=================

.. image:: https://img.shields.io/travis/inveniosoftware/flask-celeryext.svg
        :target: https://travis-ci.org/inveniosoftware/flask-celeryext

.. image:: https://img.shields.io/coveralls/inveniosoftware/flask-celeryext.svg
        :target: https://coveralls.io/r/inveniosoftware/flask-celeryext

.. image:: https://img.shields.io/github/tag/inveniosoftware/flask-celeryext.svg
        :target: https://github.com/inveniosoftware/flask-celeryext/releases

.. image:: https://img.shields.io/pypi/dm/flask-celeryext.svg
        :target: https://pypi.python.org/pypi/flask-celeryext

.. image:: https://img.shields.io/github/license/inveniosoftware/flask-celeryext.svg
        :target: https://github.com/inveniosoftware/flask-celeryext/blob/master/LICENSE

About
=====

Flask-CeleryExt is a simple integration layer between Celery and Flask.

Installation
============

Flask-CeleryExt is on PyPI so all you need is: ::

    pip install flask-celeryext

Documentation
=============

Documentation is readable at https://flask-celeryext.readthedocs.io/ or can be
build using Sphinx: ::

    pip install Sphinx
    python setup.py build_sphinx

Testing
=======

Running the test suite is as simple as: ::

    python setup.py test


Changes
=======

Version 0.3.1 (released 2018-03-26)

- Accounts for non-strict Celery versions.

Version 0.3.0 (released 2017-03-24)

- Adds support for Celery v4.

Version 0.2.2 (released 2016-11-07)

- Forces celery version to v3.1-4.0 due to problem with 4.x.

Version 0.2.1 (released 2016-07-25)

Improved features

- Improves documentation structure and its automatic generation.

Version 0.2.0 (released 2016-02-02)

Incompatible changes

- Changes celery application creation to use the default current
  celery application instead creating a new celery application. This
  addresses an issue with tasks using the shared_task decorator and
  having Flask-CeleryExt initialized multiple times.

Version 0.1.0 (released 2015-08-17)

- Initial public release


