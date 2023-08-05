"""sphinxcontrib.specs.builder

The Specializations builder.
"""

from sphinx.builders.html import StandaloneHTMLBuilder


class SpecsBuilder(StandaloneHTMLBuilder):
    name = "specs"
    search = False
