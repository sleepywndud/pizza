# this file is used to import all the modules
# you can also add variables that is going to be WIDELY used around the project

from flask import Flask, app, render_template, request, redirect, url_for
import logging
import sqlite3

# makes flask stop printing the requiest logs and startup banners
log = logging.getLogger("werkzeug")
log.disabled = True

app = Flask(__name__)
