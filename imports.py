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
