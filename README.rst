Inlinehashes
============

A small tool and library to generate the hashes of inline content that needs to be whitelisted when serving an HTML document
with a `Content-Security-Policy <https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP>`_ (because, as the name indicates,
using ``unsafe-inline`` is not recommended).

You provide the HTML content (directly or through a file path/URL) then ``inlinehashes`` will parse the document and provide
you with a list of elements that need to be explicitly added to the CSP header/tag.

The tool can be specially useful for scenarios where you use/include external software solutions in your website or application
(such as a 3rd party CMS, etc), since it will allow you to detect changes after updates and edit you CSP accordingly.

*Quick note: Always verify the content you are whitelisting and be careful when fetching live website data, since any existing
XSS code will be included in the results.*

**At the moment this package is still in a very early stage, so it still doesn't detect all possible items and the current API
might change with future releases.**

Inline content that is currently detected:

* ``<script></script>`` tags
* ``<style></style>`` tags
* Many event handlers defined in element/tag attributes
* Styles defined directly in the element/tag using the ``style`` attribute


Installation
------------

Using pip you just need to ``pip install inlinehashes``

Usage
-----

The package can be used through 2 different ways, either by using the CLI interface or programmatically in your python project.
Bellow you can find a quick summary of the available functionality.

CLI app
.......

This is the available functionality:

.. code::

  usage: inlinehashes [-h] [-a {sha256,sha384,sha512}] [-o {table,json,plain}] [-t {all,script-src,style-src}] source

  positional arguments:
    source                URL or local HTML file to check

  options:
    -h, --help            show this help message and exit
    -a {sha256,sha384,sha512}, --alg {sha256,sha384,sha512}
                          Hash algorithm to use (default: sha256)
    -o {table,json,plain}, --output {table,json,plain}
                          Format used to write the output (default: table)
    -t {all,script-src,style-src}, --target {all,script-src,style-src}
                          Target inline content to look for (default: all)

Here is an example of the output:

.. code::

    $inlinehashes https://ovalerio.net -a sha384 -o json
    [
      {
        "content": "\n      html {\n        height: 100%;\n      }\n      ",
        "hash": "sha384-Ku20lQH5qbr4EDPzXD2rf25rEHJNswNYRUNMPjYl7jCe0eHJYDe0gFdQpnKkFUTv",
        "directive": "style-src",
        "line": 12,
        "position": 0
      }
    ]


Library
.......

Here is the same example, but using python's shell:

.. code:: python

    >>> import requests
    >>> import inlinehashes
    >>> content = requests.get("https://ovalerio.net").text
    >>> inlines = inlinehashes.parse(content)
    >>> inlines
    [Inline(line='17', position='0')]
    >>> first = inlines[0]
    >>> first.short_content
    '\n      html {\n        height: 100%;\n      }\n      '
    >>> first.sha256
    'sha256-aDiwGOuSD1arNOxmHSp89QLe81yheSUQFjqpWHYCpRY='
    >>> first.sha384
    'sha384-Ku20lQH5qbr4EDPzXD2rf25rEHJNswNYRUNMPjYl7jCe0eHJYDe0gFdQpnKkFUTv'
    >>> first.sha512
    'sha512-cBO6RNy87Tx3HmpXRZUs/DPxGq9ZOqIZ9cCyDum0kNZeLEWVvW5DtYFRmHcQawnAoWeeRmll4aJeLXTb2OLBlA=='
    >>> first.content
    '\n      html {\n        height: 100%;\n      }\n      body {\n        background-image: url("data:image/png;base64,iVBORw0KGgoAAAANS...'

Contributions
-------------

All contributions and improvements are welcome.
