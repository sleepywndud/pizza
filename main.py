"""
Pizza takeaway ordering system for Domino'
Created by: James Park.
Project Started on the 1st of May, 2026.
"""

# imports everything from the imports file
from imports import *


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/snacks")
def snacks():
    return render_template("snacks.html")


@app.route("/drinks")
def drinks():
    return render_template("drinks.html")


@app.route("/customize")
def customize():
    return render_template("customize.html")


if __name__ == "__main__":
    app.run(debug=True, port=2222)
