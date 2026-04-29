"""
Main entry point for the Python application.
"""
from flask import render_template
from __init__ import app


@app.route('/', methods=['GET'])
def main() -> str:
    """Main function to run the application."""
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about() -> str:
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


@app.route('/services', methods=['GET'])
def services() -> str:
    """Services page."""
    return render_template('index.html')


@app.route('/experience', methods=['GET'])
def experience() -> str:
    """Work Experience page."""
    return render_template('index.html')


@app.route('/portfolio', methods=['GET'])
def portfolio() -> str:
    """Portfolio page."""
    return render_template('index.html')


@app.route('/contact', methods=['GET'])
def contact() -> str:
    """Contact page."""
    return render_template('index.html')


@app.route('/contact', methods=['GET']) # type: ignore
def contact() -> None:
    """Contact page."""
    return render_template('index.html')  # type: ignore


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
