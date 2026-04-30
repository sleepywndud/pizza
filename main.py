"""
Pizza takeaway ordering system for Domino'
Created by: James Park.
Project Started on the 1st of May, 2026.
"""

# imports everything from the imports file
from imports import *


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template(
        "index.html"
    )  # add variables inside the brackets later when passing variables to render template


if __name__ == "__main__":
    app.run(debug=True, port=2222)
