from os import path


def setup(app):
    abspath = path.abspath(path.dirname(__file__))
    app.add_html_theme('haruki_hw', path.join(abspath, 'haruki_hw'))