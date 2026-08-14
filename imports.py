# this file is used to import all the modules
# you can also add variables that is going to be WIDELY used around the project

from flask import Flask, app, render_template, request, redirect, url_for, flash
from colorama import Fore  # colorama is for color terminal printing
import logging  # to disable werkzeug (or whateevr) log that spams the screen
import sqlite3

# makes flask stop printing the request logs and startup banners
log = logging.getLogger("werkzeug")
log.disabled = True

app = Flask(__name__)


# total cost calculator (in case of any prices that are in irrational numbers or never-ending decimals such as 0.333...)
def totalcost_calc(orders):
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    return round(total_cost, 2)


# database connecting functions
def menu_connect(table="pizza", sort_by=None):
    # sort_by comes from the <select id="sort"> in the menu pages, e.g.
    # "price-ascending" or "rating-descending"
    sort_by = sort_by or "price-ascending"
    field, _, direction = sort_by.partition("-")

    sort_column = "rating" if field == "rating" else "price"
    sort_direction = "DESC" if direction == "descending" else "ASC"

    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()

    if table == "ingredient":
        # ingredient wasn't merged into menu_item -- still its own table
        cr.execute(f"SELECT * FROM ingredient ORDER BY {sort_column} {sort_direction}")
    else:
        # pizza/snack/drinks are now one table (menu_item) with a category
        # column, so "table" here is a category value, not a table name
        cr.execute(
            f"SELECT item_id, name, price, imageURL, rating FROM menu_item "
            f"WHERE category = ? ORDER BY {sort_column} {sort_direction}",
            (table,),
        )
    data = cr.fetchall()
    conn.close()

    return data


# connects to the cart db
def order_connect():
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    # item_id is a FK to menu_item so JOIN
    cr.execute(
        """
        SELECT cart.cart_id, cart.name, menu_item.price, cart.quantity
        FROM cart
        JOIN menu_item ON cart.item_id = menu_item.item_id
        """
    )
    orders = cr.fetchall()
    conn.close()
    return orders


# connects to the draft pizza db
def draft_connect():
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    # ingredient_id is a FK to ingredient so JOIN
    cr.execute(
        """
        SELECT custom_pizza_draft.draft_id, ingredient.name, ingredient.price
        FROM custom_pizza_draft
        JOIN ingredient ON custom_pizza_draft.ingredient_id = ingredient.ingredient_id
        WHERE custom_pizza_draft.item_id IS NULL
        """
    )
    draft = cr.fetchall()
    conn.close()

    return draft


# connects to the voucher db
def voucher_connect():
    # returns the currently applied voucher as (code, discount_percentage), or None if none applied
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    # id = 1 checks if ANY data exists in the table
    cr.execute(
        "SELECT voucher_code, discount_percentage FROM applied_voucher WHERE voucher_id = 1"
    )
    voucher = cr.fetchone()
    conn.close()

    return voucher


# function to apply voucher to the current price
def apply_voucher(code):
    # looks up the code and stores it as the applied voucher
    # returns True if the code was valid and got applied, False otherwise
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute(
        "SELECT discount_percentage FROM voucher WHERE voucher_code = ?", (code,)
    )
    voucher_data = cr.fetchone()

    #  catches all non-existing voucher codes and returns nothing (False)
    if voucher_data is None:
        conn.close()
        return False  # could add error msg in future for invalid voucher codes

    # gets the data -- [0] used since it's a tuple
    discount_percentage = voucher_data[0]

    # replaces existing voucher that's applied with new voucher
    cr.execute("DELETE FROM applied_voucher WHERE voucher_id = 1")
    cr.execute(
        "INSERT INTO applied_voucher (voucher_id, voucher_code, discount_percentage) VALUES (1, ?, ?)",
        (code, discount_percentage),
    )

    conn.commit()
    conn.close()

    return True


# function to remove the applied voucher
def remove_voucher():
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute(
        "DELETE FROM applied_voucher WHERE voucher_id = 1"
    )  # uses id=1 to remove any existing [1] vouchers
    conn.commit()
    conn.close()


# function for applying discount and rounding to 2dp
def apply_discount(total_cost, voucher):
    # applies the voucher discount % to total cost then 2dp rounding
    if voucher is None:
        return total_cost
    discount_percentage = voucher[1]
    discounted = total_cost * (1 - discount_percentage / 100)
    return round(discounted, 2)


# function to search ALL the items (from all categories)
def search_menu(query, sort_by=None):
    like_query = f"%{query}%"

    # sort_by comes from the <select id="sort"> in search.html, e.g.
    # "price-ascending" or "rating-descending"
    sort_by = sort_by or "price-ascending"
    field, _, direction = sort_by.partition("-")

    # if the query names a whole category (e.g. "drinks" or "snack"), match
    # every row in that category instead of filtering by name

    # [FIX After Bobo's trial]:
    # table names and their aliases
    table_names = {
        "pizza": "pizza",
        "snack": "snack",
        "snacks": "snack",
        "drinks": "drinks",
    }  # this prevents users from searching "pizza", and getting no results
    category_table = table_names.get(query)

    #  bunch of ifs to determine sorting configs
    if category_table == "pizza":
        pizza_query = "%"
    else:
        pizza_query = like_query

    if category_table == "snack":
        snack_query = "%"
    else:
        snack_query = like_query

    if category_table == "drinks":
        drinks_query = "%"
    else:
        drinks_query = like_query

    if field == "rating":
        sort_column = "rating"
    else:
        sort_column = "price"

    if direction == "descending":
        sort_direction = "DESC"
    else:
        sort_direction = "ASC"

    # pizza/snack/drinks used to be 3 separate tables joined with UNION ALL.
    # now they're all rows in menu_item, so we UNION ALL the same category
    # 3 times instead -- same shape as before, just querying one table
    # using this as a var because the code is too long to fit in the execute
    sql = f"""
        SELECT item_id, name, price, imageURL, 'pizza/' AS folder, rating FROM menu_item WHERE category = 'pizza' AND name LIKE ?
        UNION ALL
        SELECT item_id, name, price, imageURL, 'snacks/' AS folder, rating FROM menu_item WHERE category = 'snack' AND name LIKE ?
        UNION ALL
        SELECT item_id, name, price, imageURL, 'drinks/' AS folder, rating FROM menu_item WHERE category = 'drinks' AND name LIKE ?
        ORDER BY {sort_column} {sort_direction}
    """

    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute(sql, (pizza_query, snack_query, drinks_query))
    rows = (
        cr.fetchall()
    )  # this 'rows' var holds ALL matching rows from the three categories
    conn.close()

    # note that folder marks which category the row came from -- it's only used to make the image display
    # without the folder variable, since the image's location in the directory varies,
    # it will make image rendering difficult due to its path not being clear

    # each row is (id, name, price, imageURL, folder, rating); combine
    # folder+imageURL into one path so templates get (id, name, price, image_path, rating)
    results = []
    for item_id, name, price, image, folder, rating in rows:
        results.append((item_id, name, price, folder + image, rating))
    return results
