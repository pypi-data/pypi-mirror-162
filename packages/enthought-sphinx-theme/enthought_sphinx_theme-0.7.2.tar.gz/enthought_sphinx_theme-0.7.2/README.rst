enthought-sphinx-theme
======================

`Sphinx <http://sphinx-doc.org>`_ theme for `Enthought projects
<http://www.enthought.com>`_, derived from the `Scipy theme
<https://github.com/scipy/scipy-sphinx-theme>`_.


Installation
------------

Install this as a normal Python package. The theme files are in the package
data.

In your project's ``conf.py`` file, do the following::

    import enthought_sphinx_theme
    html_theme_path = [enthought_sphinx_theme.theme_path]
    html_theme = 'enthought'


Theme options
-------------

The theme takes the followin options in the ``html_theme_options``
configuration variable:

- ``rootlinks``

  List of tuples ``(url, link_name)`` to show in the beginning of the
  breadcrumb list on the top left. You can override it by defining an
  `edit_link` block in ``searchbox.html``.

- ``sidebar``

  One of ``"left"``, ``"right"``, ``"none"``.  Defines where the sidebar
  should appear.

- ``navigation_links``

  ``True`` or ``False``. Whether to display "next", "prev", "index", etc.
  links.

- ``use_default_logo``

  ``True`` or ``False``. Whether to use the default Enthought logo in the
  sidebar. If the ``html_logo`` configuration parameter is non-empty, it will
  override this. Set this to ``False`` and ``html_logo`` to empty only if you
  want no logo at all.

- ``use_default_favicon``

  ``True`` or ``False``. Whether to use the default Enthought logo as the
  favicon.  If the ``html_favicon`` configuration parameter is non-empty, it
  will override this. Set this to ``False`` and ``html_favicon`` to empty only
  if you want no favicon at all.

The following blocks are defined:

- ``layout.html:header``
   
  Block at the top of the page, for logo etc.
