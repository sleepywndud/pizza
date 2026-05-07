"""
Pizza takeaway ordering system for Domino'
Created by: James Park.
Project Started on the 1st of May, 2026.
"""

# NOTE: run THIS specific Python file to run the program!

# imports all the Python modules used in this project
from imports import *

# imports all (page) routes and all the variables that is used
from routes import *

conn = sqlite3.connect("order.db")
cr = conn.cursor()
cr.execute("DELETE FROM orders")
conn.commit()
conn.close()

# starts the app when this python file is ran in http://127.0.0.1:2222/
if __name__ == "__main__":
    app.run(
        debug=True, port=2222
    )  # debug=True makes it so that live changes are observed
