"""
Pizza takeaway ordering system!
Created by: Juyoung (James) Park

Project Started on the 1st of May, 2026.
Project Due on the 14th of August, 2026.
"""

# NOTE: run THIS specific Python file to run the program!

# For whoever that's going to read the code:
# This program is split into routes.py and imports.py (for the backend)
# - routes.py has all the routes required for the Flask
# - imports.py has all the functions and variables required to run the program :)

# imports everything from imports.py and routes.py
from imports import *
from routes import *

conn = sqlite3.connect("pizza.db")
cr = conn.cursor()

# empties the cart/draft/voucher tables when program is ran
# (custom_pizza_draft is deleted first since its rows link to cart)
cr.execute("DELETE FROM custom_pizza_draft")
cr.execute("DELETE FROM cart")
cr.execute("DELETE FROM applied_voucher")
conn.commit()
conn.close()

# clears the last query and sorting order (defaults)
last_query = ""
last_sort_by = ""

# RUN!
if __name__ == "__main__":
    # test loggings NOTE: REMOVE this before submitting!!!
    print(Fore.GREEN + "\n[+] Program reloaded with latest change!" + Fore.RESET)
    print(Fore.GREEN + "[+] Visit http://localhost:2222/ for program! \n" + Fore.RESET)

    # run at localhost:2222
    app.run(debug=True, port=2222)
