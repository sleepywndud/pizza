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
