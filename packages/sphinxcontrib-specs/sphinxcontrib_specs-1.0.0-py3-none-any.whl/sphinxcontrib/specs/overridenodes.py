"""THIS IS SO GROSS I'M SORRY."""

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.writers.html5 import HTML5Translator


super_visit_hint = HTML5Translator.visit_hint
super_depart_hint = HTML5Translator.depart_hint
super_visit_title = HTML5Translator.visit_title
super_depart_title = HTML5Translator.depart_title


def visit_title(self, node: nodes.title):
    if isinstance(node.parent, nodes.hint) and node.parent.index(node) == 0:
        raise nodes.SkipNode

    if isinstance(node.parent, nodes.section):
        if str(node) == getattr(self, "_previous_title", ""):
            raise nodes.SkipNode

        self._previous_title = str(node)

    super_visit_title(self, node)


def depart_title(self, node: nodes.title):
    super_depart_title(self, node)
    if isinstance(node.parent, nodes.hint):
        self.body.append('<details class="admonition-body">')
        self.body.append("<summary></summary>")


def visit_hint(self, node: nodes.hint):
    super_visit_hint(self, node)


def depart_hint(self, node: nodes.hint):
    self.body.append("</details>")
    super_depart_hint(self, node)


def setup(app: Sphinx) -> None:
    app.add_node(
        nodes.title,
        html=(visit_title, depart_title),
        override=True,
    )
    app.add_node(
        nodes.hint,
        html=(visit_hint, depart_hint),
        override=True,
    )
