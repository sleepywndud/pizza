"""
Pizza takeaway ordering system for Domino'
Created by: James Park.
Project Started on the 1st of May, 2026.
"""

# NOTE: run THIS specific Python file to run the program!

from imports import *
from routes import *

conn = sqlite3.connect("order.db")
cr = conn.cursor()
# empties the database data in order.db when program is ran
cr.execute("DELETE FROM cart")
conn.commit()
conn.close()

if __name__ == "__main__":
    print(Fore.GREEN + "[+] Program reloaded!" + Fore.RESET)
    app.run(debug=True, port=2222)
