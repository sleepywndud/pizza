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

    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute(f"SELECT * FROM {table} ORDER BY {sort_column} {sort_direction}")
    data = cr.fetchall()
    conn.close()

    return data


def order_connect():
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute("SELECT * FROM cart")
    orders = cr.fetchall()
    conn.close()

    return orders


def draft_connect():
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute("SELECT * FROM custom_pizza_draft")
    draft = cr.fetchall()
    conn.close()

    return draft


def voucher_connect():
    # returns the currently applied voucher as (code, discount_percentage), or None if none applied
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    # id = 1 checks if ANY data exists in the table
    cr.execute("SELECT code, discount_percentage FROM applied_voucher WHERE id = 1")
    voucher = cr.fetchone()
    conn.close()

    return voucher


def apply_voucher(code):
    # looks up the code in database.db and stores it as the applied voucher in order.db
    # returns True if the code was valid and got applied, False otherwise
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute("SELECT discount_percentage FROM voucher WHERE code = ?", (code,))
    voucher_data = cr.fetchone()
    conn.close()

    #  catches all non-existing voucher codes and returns nothing (False)
    if voucher_data is None:
        return False  # could add error msg in future for invalid voucher codes

    # gets the data -- [0] used since it's a tuple
    discount_percentage = voucher_data[0]

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()

    # replaces existing voucher that's applied with new voucher
    cr.execute("DELETE FROM applied_voucher WHERE id = 1")
    cr.execute(
        "INSERT INTO applied_voucher (id, code, discount_percentage) VALUES (1, ?, ?)",
        (code, discount_percentage),
    )

    conn.commit()
    conn.close()

    return True


def remove_voucher():
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute("DELETE FROM applied_voucher WHERE id = 1")
    conn.commit()
    conn.close()


def apply_discount(total_cost, voucher):
    # applies the voucher discount % to total cost then 2dp rounding
    if voucher is None:
        return total_cost
    discount_percentage = voucher[1]
    discounted = total_cost * (1 - discount_percentage / 100)
    return round(discounted, 2)


def search_menu(query, sort_by=None):
    like_query = f"%{query}%"

    # sort_by comes from the <select id="sort"> in search.html, e.g.
    # "price-ascending" or "rating-descending"
    sort_by = sort_by or "price-ascending"
    field, _, direction = sort_by.partition("-")

    # if the query names a whole category (e.g. "drinks" or "snack"), match
    # every row in that table instead of filtering by name

    # table names and their aliases; NOTE: might be better if changed in the fture
    table_names = {
        "pizza": "pizza",
        "snack": "snack",
        "snacks": "snack",
        "drinks": "drinks",
    }
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

    # using multiple queries (from multiple tables) using UNION ALL
    # using this as a var because the code is too long to fit in the execute
    sql = f"""
        SELECT id, name, price, imageURL, 'pizza/' AS folder FROM pizza WHERE name LIKE ?
        UNION ALL
        SELECT id, name, price, imageURL, 'snacks/' AS folder FROM snack WHERE name LIKE ?
        UNION ALL
        SELECT id, name, price, imageURL, 'drinks/' AS folder FROM drinks WHERE name LIKE ?
        ORDER BY {sort_column} {sort_direction}
    """

    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute(sql, (pizza_query, snack_query, drinks_query))
    rows = cr.fetchall()
    conn.close()

    # each row is (id, name, price, imageURL, folder); combine folder+imageURL
    # into one path so templates get (id, name, price, image_path)
    results = []
    for item_id, name, price, image, folder in rows:
        results.append((item_id, name, price, folder + image))
    return results
