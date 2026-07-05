from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .auth import auth as auth_blueprint


main = Blueprint('main', __name__)

#Replace routes/functions/returns with your unique values
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/plantDoc')
def plantDox():
    return render_template('plantDOc.html')


'Add as needed'