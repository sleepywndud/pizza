"""
Pizza takeaway ordering system for Domino'
Created by: James Park.
Project Started on the 1st of May, 2026.
"""

# imports everything from the imports file
from imports import *


@app.route("/", methods=["GET", "POST"])
def main():
    return "Hello world"


if __name__ == "__main__":
    app.run(debug=True, port=2222)
