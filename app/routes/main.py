from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("profile.dashboard"))

    return render_template("index.html")


@main_bp.route("/home")
def home():
    return redirect(url_for("main.index"))