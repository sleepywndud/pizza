# this file is used to import all the modules
# you can also add variables that is going to be WIDELY used around the project

from flask import Flask, app, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
