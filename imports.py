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
def menu_connect(table="pizza"):
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute(f"SELECT * FROM {table}")
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

    #  catches all non-existing voucher codes
    if voucher_data is None:
        return False

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
