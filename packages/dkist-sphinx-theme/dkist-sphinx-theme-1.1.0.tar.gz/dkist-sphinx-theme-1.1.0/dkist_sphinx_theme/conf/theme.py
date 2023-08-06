import os

from dkist_sphinx_theme import get_html_theme_path

html_theme_path = get_html_theme_path()

html_theme = "dkist"

html_theme_options = {
    "navbar_links": [
        ("DKIST Home", "https://nso.edu/telescopes/dki-solar-telescope/", 1),
        ("Python Tools", "https://docs.dkist.nso.edu/projects/python-tools/", 1),
        ("Calibration", "https://docs.dkist.nso.edu/en/latest/calibration.html", 1),
        ("Data Products", "https://docs.dkist.nso.edu/projects/data-products/", 1)
        # Other DKIST Resources when live
        # ("Data Portal", "enter correct url here", 1),
        # ("Help Desk", "enter correct url here", 1),
    ]
}
html_favicon = os.path.join(
    html_theme_path[0],
    html_theme,
    "static",
    "img",
    "favico.ico",
)

html_sidebars = {
    "**": ["localtoc.html"],
    "search": [],
    "genindex": [],
    "py-modindex": [],
}
