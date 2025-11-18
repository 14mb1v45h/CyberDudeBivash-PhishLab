# backend/routes_auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash

auth = Blueprint("auth", __name__)

@auth.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        cfg = current_app.config
        if username == cfg.get("ADMIN_USERNAME") and password == cfg.get("ADMIN_PASSWORD"):
            session["admin_logged_in"] = True
            # Optional: store username
            session["admin_username"] = username

            next_url = request.args.get("next") or url_for("admin.admin_dashboard")
            return redirect(next_url)
        else:
            # you can use flash messages if you want; for now just re-render
            error = "Invalid username or password"
            return render_template("admin_login.html", error=error)

    # GET
    return render_template("admin_login.html", error=None)


@auth.route("/admin/logout", methods=["POST", "GET"])
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect(url_for("auth.admin_login"))
