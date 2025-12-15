"""
Main entry point for the Python application.
"""
from flask import render_template
from __init__ import app


@app.route('/', methods=['GET']) # type: ignore
def main() -> None:
    """Main function to run the application."""
    return render_template('index.html')  # type: ignore


@app.route('/about', methods=['GET']) # type: ignore
def about() -> None:
    """About page."""
    return render_template('about.html')  # type: ignore


@app.route('/services', methods=['GET']) # type: ignore
def services() -> None:
    """Services page."""
    return render_template('index.html')  # type: ignore


@app.route('/experience', methods=['GET']) # type: ignore
def experience() -> None:
    """Work Experience page."""
    return render_template('index.html')  # type: ignore


@app.route('/portfolio', methods=['GET']) # type: ignore
def portfolio() -> None:
    """Portfolio page."""
    return render_template('index.html')  # type: ignore


@app.route('/contact', methods=['GET']) # type: ignore
def contact() -> None:
    """Contact page."""
    return render_template('index.html')  # type: ignore


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
