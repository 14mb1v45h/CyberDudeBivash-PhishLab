@app.route("/t/<token>", methods=["GET"])
def training_landing(token):
    target = Target.query.filter_by(token=token).first()
    if not target:
        abort(404)

    # Log click event once
    if target.status == "not_clicked":
        target.status = "clicked"
        target.first_clicked_at = datetime.utcnow()
        ev = Event(campaign_id=target.campaign_id,
                   target_id=target.id,
                   type="clicked",
                   user_agent=request.headers.get("User-Agent"),
                   ip=request.remote_addr)
        db.session.add(ev)
        db.session.commit()

    return render_template("landing_generic.html", target=target)

@app.route("/t/<token>/submit", methods=["POST"])
def training_submit(token):
    target = Target.query.filter_by(token=token).first()
    if not target:
        abort(404)

    # We intentionally ignore actual form values – training only
    # username = request.form.get("username")
    # password = request.form.get("password")
    # DO NOT log/store these.

    if target.status in ("not_clicked", "clicked"):
        target.status = "submitted"
        target.first_submitted_at = datetime.utcnow()

        ev = Event(campaign_id=target.campaign_id,
                   target_id=target.id,
                   type="submitted",
                   user_agent=request.headers.get("User-Agent"),
                   ip=request.remote_addr)
        db.session.add(ev)

    db.session.commit()
    return render_template("landing_success.html", target=target)
