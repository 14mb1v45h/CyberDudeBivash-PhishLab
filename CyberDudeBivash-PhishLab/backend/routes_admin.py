# backend/routes_admin.py

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from .models import Campaign, Target
from .extensions import db
import secrets
import csv
import io
from flask import Blueprint, request, jsonify, render_template, make_response
from datetime import datetime
from .models import Campaign, Target
from .extensions import db
import secrets
from flask import Blueprint, request, jsonify, render_template, make_response, session, redirect, url_for
from functools import wraps


admin = Blueprint("admin", __name__)

def admin_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            # send them to login with a `next` parameter
            return redirect(url_for("auth.admin_login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


admin = Blueprint("admin", __name__)

@admin.route("/admin/campaigns", methods=["GET"])
@admin_login_required
def list_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "created_at": c.created_at.isoformat()}
        for c in campaigns
    ])

@admin.route("/admin/campaigns", methods=["POST"])
@admin_login_required
def create_campaign():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "name required"}), 400

    c = Campaign(name=name, description=description)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name}), 201

@admin.route("/admin/campaigns/<int:cid>/targets", methods=["POST"])
@admin_login_required
def add_targets(cid):
    campaign = Campaign.query.get_or_404(cid)
    data = request.get_json() or {}
    targets = data.get("targets", [])

    created = []
    for t in targets:
        token = secrets.token_urlsafe(16)
        target = Target(
            campaign_id=campaign.id,
            email=t["email"],
            name=t.get("name"),
            token=token
        )
        db.session.add(target)
        created.append({
            "email": target.email,
            "name": target.name,
            "token": target.token,
            "link": f"/t/{target.token}",
        })
    db.session.commit()
    return jsonify(created), 201


# 🔥 NEW: Dashboard UI
@admin.route("/admin/dashboard", methods=["GET"])
@admin_login_required
def admin_dashboard():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    rows = []

    for c in campaigns:
        total = len(c.targets)
        clicked = sum(1 for t in c.targets if t.status in ("clicked", "submitted", "reported"))
        submitted = sum(1 for t in c.targets if t.status in ("submitted", "reported"))
        reported = sum(1 for t in c.targets if t.status == "reported")

        rows.append({
            "id": c.id,
            "name": c.name,
            "created_at": c.created_at,
            "total": total,
            "clicked": clicked,
            "submitted": submitted,
            "reported": reported,
        })

    return render_template("admin_dashboard.html", campaigns=rows)

@admin.route("/admin/campaigns/<int:cid>/targets/upload-csv", methods=["POST"])
@admin_login_required
def upload_targets_csv(cid):
    """
    Accepts multipart/form-data with a file field named 'file'.
    CSV must have headers: email,name
    """
    campaign = Campaign.query.get_or_404(cid)

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file field is required"}), 400

    try:
        # Read CSV as text
        stream = io.StringIO(file.stream.read().decode("utf-8"))
    except UnicodeDecodeError:
        return jsonify({"error": "Could not decode file as UTF-8"}), 400

    reader = csv.DictReader(stream)
    if "email" not in reader.fieldnames:
        return jsonify({"error": "CSV must include 'email' column"}), 400

    created = 0
    skipped = 0
    targets_out = []

    for row in reader:
        email = (row.get("email") or "").strip()
        name = (row.get("name") or "").strip() if "name" in row else None

        if not email:
            skipped += 1
            continue

        token = secrets.token_urlsafe(16)
        t = Target(
            campaign_id=campaign.id,
            email=email,
            name=name or None,
            token=token
        )
        db.session.add(t)
        created += 1
        targets_out.append({
            "email": email,
            "name": name,
            "token": token,
            "link": f"/t/{token}"
        })

    db.session.commit()

    return jsonify({
        "campaign_id": campaign.id,
        "created": created,
        "skipped": skipped,
        "targets": targets_out
    }), 201
@admin.route("/admin/campaigns/<int:cid>/export.csv", methods=["GET"])
@admin_login_required
def export_campaign_csv(cid):
    """
    Returns a CSV of all targets for a campaign with their simulation status.
    """
    campaign = Campaign.query.get_or_404(cid)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "email",
        "name",
        "status",
        "first_clicked_at",
        "first_submitted_at",
        "training_link"
    ])

    for t in campaign.targets:
        writer.writerow([
            t.email,
            t.name or "",
            t.status,
            t.first_clicked_at.isoformat() if t.first_clicked_at else "",
            t.first_submitted_at.isoformat() if t.first_submitted_at else "",
            f"/t/{t.token}",
        ])

    csv_data = output.getvalue()
    output.close()

    resp = make_response(csv_data)
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = (
        f"attachment; filename=campaign_{campaign.id}_targets.csv"
    )
    return resp
@admin.route("/admin/campaigns/<int:cid>/upload", methods=["GET"])
@admin_login_required
def upload_page(cid):
    campaign = Campaign.query.get_or_404(cid)
    return render_template("upload_targets.html", campaign=campaign)

@admin.route("/admin/campaigns/<int:cid>", methods=["GET"])
@admin_login_required
def campaign_detail(cid):
    campaign = Campaign.query.get_or_404(cid)

    # stats
    total = len(campaign.targets)
    clicked = sum(1 for t in campaign.targets if t.status in ("clicked", "submitted", "reported"))
    submitted = sum(1 for t in campaign.targets if t.status in ("submitted", "reported"))
    reported = sum(1 for t in campaign.targets if t.status == "reported")

    # prepare rows for table
    target_rows = []
    for t in campaign.targets:
        target_rows.append({
            "email": t.email,
            "name": t.name or "",
            "status": t.status,
            "clicked": t.first_clicked_at.strftime("%Y-%m-%d %H:%M") if t.first_clicked_at else "",
            "submitted": t.first_submitted_at.strftime("%Y-%m-%d %H:%M") if t.first_submitted_at else "",
            "link": f"/t/{t.token}",
        })

    return render_template(
        "campaign_detail.html",
        campaign=campaign,
        total=total,
        clicked=clicked,
        submitted=submitted,
        reported=reported,
        targets=target_rows
    )

@admin.route("/admin/targets/<int:tid>", methods=["GET"])
@admin_login_required
def target_detail(tid):
    target = Target.query.get_or_404(tid)
    campaign = target.campaign

    # Sort events newest → oldest
    events = sorted(target.events, key=lambda e: e.timestamp, reverse=True)

    event_rows = []
    for ev in events:
        event_rows.append({
            "type": ev.type,
            "timestamp": ev.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ev.ip or "",
            "ua": ev.user_agent or "",
        })

    return render_template(
        "target_detail.html",
        target=target,
        campaign=campaign,
        events=event_rows,
    )


