========
WaporIHE
========

This is the documentation of **WaporIHE**.

From the root of the project, run::

    python setup.py --version

Format scripts by PEP8

    autopep8 --in-place --aggressive src/WaporIHE/WaporAPI.py

Unit test, run::

    python setup.py test

Read the Docs, run::

    python setup.py doctest

    python setup.py docs

PyPI upload, run ``setup.py``::

    1. Commit -> Git - tag - add - v0.0.1 -> ``setup.py`` -> push
    2. Github - Release - new release v0.0.1

    python setup.py sdist bdist_wheel
    twine check dist/*.tar.gz
    twine upload dist/*

.. warning::

    Must contain **config.yml** and **accounts.yml-encrypted** file.

.. note::

    This is the main page of your project's `Sphinx`_ documentation.
    It is formatted in `reStructuredText`_. Add additional pages
    by creating rst-files in ``docs`` and adding them to the `toctree`_ below.
    Use then `references`_ in order to link them from this page, e.g.
    :ref:`authors` and :ref:`changes`.

    It is also possible to refer to the documentation of other Python packages
    with the `Python domain syntax`_. By default you can reference the
    documentation of `Sphinx`_, `Python`_, `NumPy`_, `SciPy`_, `matplotlib`_,
    `Pandas`_, `Scikit-Learn`_. You can add more by extending the
    ``intersphinx_mapping`` in your Sphinx's ``conf.py``.

    The pretty useful extension `autodoc`_ is activated by default and lets
    you include documentation from docstrings. Docstrings can be written in
    `Google style`_ (recommended!), `NumPy style`_ and `classical style`_.


Contents
========

.. toctree::
   :maxdepth: 4

   License <license>
   Authors <authors>
   Contributing <contributing>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
