Graphviz utility functions.

*Latest release 20220805.1*:
New DOTNodeMixin, a mixin for classes which can be rendered as a DOT node.

See also the [https://www.graphviz.org/documentation/](graphviz documentation)
and particularly the [https://graphviz.org/doc/info/lang.html](DOT language specification)
and the [https://www.graphviz.org/doc/info/command.html](`dot` command line tool).

## Class `DOTNodeMixin`

A mixin providing methods for things which can be drawn as
nodes in a DOT graph description.

*Method `DOTNodeMixin.dot_node(self, label=None, **node_attrs) -> str`*:
A DOT syntax node definition for `self`.

*Method `DOTNodeMixin.dot_node_attrs(self) -> Mapping[str, str]`*:
The default DOT node attributes.

*Method `DOTNodeMixin.dot_node_label(self) -> str`*:
The default node label.
This implementation returns `str(serlf)`
and a common implementation might return `self.name` or similar.

## Function `gvprint(dot_s, file=None, fmt=None, layout=None, **dot_kw)`

Print the graph specified by `dot_s`, a graph in graphViz DOT syntax,
to `file` (default `sys.stdout`)
in format `fmt` using the engine specified by `layout` (default `'dot'`).

If `fmt` is unspecified it defaults to `'png'` unless `file`
is a terminal in which case it defaults to `'sixel'`.

This uses the graphviz utility `dot` to draw graphs.
If printing in SIXEL format the `img2sixel` utility is required,
see [https://saitoha.github.io/libsixel/](libsixel).

## Function `quote(s)`

Quote a string for use in DOT syntax.
This implementation passes identifiers and sequences of decimal numerals
through unchanged and double quotes other strings.

# Release Log



*Release 20220805.1*:
New DOTNodeMixin, a mixin for classes which can be rendered as a DOT node.

*Release 20220805*:
Initial PyPI release.
