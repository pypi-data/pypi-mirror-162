from os import path


themes = [
    'haruki_hw',
]

def setup(app):
    abspath = path.abspath(path.dirname(__file__))
    for theme in themes:
        app.add_html_theme(theme, path.join(abspath, f'{theme}_theme'))