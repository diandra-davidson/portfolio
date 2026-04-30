"""
Main entry point for the Python application.
"""
from flask import render_template, Blueprint
from __init__ import app


bp = Blueprint("main", __name__)


@bp.get('/')
def main() -> None:
    """Main function to run the application."""
    return render_template('index.html')


@bp.get('/about')
def about() -> None:
    """About page."""
    return render_template('about.html')

  
@bp.get('/services')
def services() -> None:
    """Services page."""
    return render_template('index.html') # type: ignore


@bp.get('/experience')
def experience() -> None:
    """Work Experience page."""
    return render_template('index.html')


@bp.get('/portfolio')
def portfolio() -> None:
    """Portfolio page."""
    return render_template('index.html')


@bp.get('/contact')
def contact() -> None:
    """Contact page."""
    return render_template('index.html')
