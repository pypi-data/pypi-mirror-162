Graphviz utility functions.

*Latest release 20220805*:
Initial PyPI release.

See also the [https://www.graphviz.org/documentation/](graphviz documentation)
and particularly the [https://graphviz.org/doc/info/lang.html](DOT language specification)
and the [https://www.graphviz.org/doc/info/command.html](`dot` command line tool).

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



*Release 20220805*:
Initial PyPI release.
