import functools


def joins(function):
    @functools.wraps(function)
    def inner(*args, **kwargs):
        return "".join(function(*args, **kwargs))

    return inner


def css_string(css):
    """Convert a dictionary to a CSS string."""
    return ";".join(f"{p}:{v}" for p, v in css.items())


def a(string, href):
    return f'<a href="{href}">{string}</a>'


def th(string=""):
    return f"<th>{string}</th>"


def td(string="", /, *, align="l", class_=None, colour=None, text_colour=None):
    """Wrap a string with <td> tags to make it a table cell."""
    css = {}
    align = {"c": "center", "r": "right", "l": "left"}[align[0].casefold()]
    if align != "left":
        css["text-align"] = align
    if colour is not None:
        css["background-color"] = f"#{colour.upper()}"
    if text_colour is not None:
        css["color"] = f"#{text_colour.upper()}"
    css_str = f' style="{css_string(css)}"' if css else ""
    class_str = f' class="{class_}"' if class_ is not None else ""
    return f"<td{class_str}{css_str}>{string}</td>"


@joins
def create_html_table(data, class_=None):
    """Make an HTML table string from lists of data."""
    class_ = f' class="{class_}"' if class_ is not None else ""
    yield f"<table{class_}><thead>"
    for i, row in enumerate(data):
        if isinstance(row, str):
            yield row
        else:
            yield "<tr>"
            yield from (str(x) for x in row)
            yield "</tr>"
        if i == 0:
            yield "</thead><tbody>"
    yield "</tbody></table>"
