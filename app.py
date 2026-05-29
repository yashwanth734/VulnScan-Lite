from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery
from celery.result import AsyncResult
from flask_talisman import Talisman
import os
import logging

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- App and extensions ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'yoursecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///scans.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Celery config via env or defaults
app.config.setdefault('CELERY_BROKER_URL', os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))
app.config.setdefault('CELERY_RESULT_BACKEND', os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=app.config['CELERY_BROKER_URL']
)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth"

# --- Security headers via Flask-Talisman ---
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://unpkg.com", "https://fonts.googleapis.com"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://fonts.gstatic.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com", "https://fonts.googleapis.com"],
    'img-src': ["'self'", "data:"],
    'connect-src': ["'self'"],
}
# force_https=False for local development; set True in production
Talisman(app, content_security_policy=csp, force_https=False, strict_transport_security=False)

# Fallback: ensure headers always present and log for debugging
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self';"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    try:
        logger.info(
            "Security headers applied: X-Frame-Options=%s, CSP=%s, HSTS=%s",
            response.headers.get("X-Frame-Options"),
            response.headers.get("Content-Security-Policy"),
            response.headers.get("Strict-Transport-Security"),
        )
    except Exception:
        pass
    return response

# Explicitly register the after_request handler so it is guaranteed to be attached
app.after_request(set_security_headers)

# Celery must be defined before any @celery.task decorator
celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

# --- Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), unique=True, nullable=True)
    url = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer)
    grade = db.Column(db.String(5))
    issues = db.Column(db.Text)
    passed_checks = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

# --- Routes ---
@app.route('/')
def home():
    return "App is running"

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/history', methods=['GET'])
@login_required
def history():
    scans = ScanResult.query.filter_by(user_id=current_user.id).order_by(ScanResult.id.desc()).all()
    return jsonify([{
        "task_id": s.task_id,
        "url": s.url,
        "score": s.score,
        "grade": s.grade,
        "timestamp": s.timestamp.isoformat()
    } for s in scans])

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action', 'login')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        
        if action == 'signup':
            if not username or not password:
                flash('Please provide both username and password.', 'danger')
                return redirect(url_for('auth'))
            if password != confirm:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth'))
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Try logging in.', 'danger')
                return redirect(url_for('auth'))
            hashed = generate_password_hash(password)
            user = User(username=username, password=hashed)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('auth'))
            
        elif action == 'forgot':
            if not username or not password:
                flash('Please provide username and new password.', 'danger')
                return redirect(url_for('auth'))
            if password != confirm:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth'))
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('No account registered with that username.', 'danger')
                return redirect(url_for('auth'))
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Password reset successfully! You can now login.', 'success')
            return redirect(url_for('auth'))
            
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('No account registered with that username.', 'danger')
                return redirect(url_for('auth'))
            if not check_password_hash(user.password, password):
                flash('Wrong password. Please try again.', 'danger')
                return redirect(url_for('auth'))
            login_user(user)
            return redirect(url_for('dashboard'))
            
    return render_template('auth.html')

@app.route('/api/scan', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def start_scan():
    import urllib.parse
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing url"}), 400
        
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return jsonify({"error": "Invalid URL. Please enter a valid website starting with http:// or https://"}), 400
        
    task = run_scan.delay(url, current_user.id)
    return jsonify({"task_id": task.id}), 202

@app.route('/api/scan/<task_id>/status', methods=['GET'])
@login_required
def scan_status(task_id):
    task = AsyncResult(task_id, app=celery)
    return jsonify({"state": task.state, "result": task.result if task.state == "SUCCESS" else None})

@app.route('/api/report/<task_id>/json', methods=['GET'])
@login_required
def report_json(task_id):
    from scanner.remediation import get_remediation_tips
    
    row = ScanResult.query.filter_by(task_id=task_id, user_id=current_user.id).first()
    if row:
        issues = row.issues.split("; ") if row.issues else []
        return jsonify({
            "task_id": row.task_id,
            "url": row.url,
            "score": row.score,
            "grade": row.grade,
            "issues": issues,
            "passed_checks": row.passed_checks.split("; ") if row.passed_checks else [],
            "remediation": get_remediation_tips(issues),
            "timestamp": row.timestamp.isoformat()
        })
    recent = ScanResult.query.filter_by(user_id=current_user.id).order_by(ScanResult.id.desc()).first()
    if recent:
        issues = recent.issues.split("; ") if recent.issues else []
        return jsonify({
            "task_id": recent.task_id,
            "url": recent.url,
            "score": recent.score,
            "grade": recent.grade,
            "issues": issues,
            "passed_checks": recent.passed_checks.split("; ") if recent.passed_checks else [],
            "remediation": get_remediation_tips(issues),
            "timestamp": recent.timestamp.isoformat(),
            "note": "Returned most recent scan for user because task_id was not found"
        })
    task = AsyncResult(task_id, app=celery)
    if task.state == 'SUCCESS' and task.result:
        res = task.result
        res["remediation"] = get_remediation_tips(res.get("issues", []))
        return jsonify(res)
    return jsonify({"error": "Report not found"}), 404

# --- Scanner Celery task ---
@celery.task(bind=True, name="run_scan")
def run_scan(self, url, user_id):
    from scanner import check_headers, check_ssl, detect_cms

    task_id = getattr(self.request, "id", None)
    logger.info("run_scan started task_id=%s url=%s user_id=%s", task_id, url, user_id)

    issues, score, grade = [], 100, "A"
    passed_checks = []

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # 1. Header Analysis
    header_res = check_headers(url)
    if not header_res["ok"]:
        err_msg = header_res.get("error", "")
        err_msg_lower = err_msg.lower()
        connection_indicators = [
            "failed to establish a new connection",
            "getaddrinfo failed",
            "connectionerror",
            "max retries exceeded",
            "nameresolutionerror",
            "name or service not known",
            "connection refused",
            "dns",
            "unreachable"
        ]
        if any(indicator in err_msg_lower for indicator in connection_indicators):
            issues.append("Website is not found")
            score = 0
            grade = "F"
            # Save and return immediately
            try:
                with app.app_context():
                    new_scan = ScanResult(
                        task_id=task_id, url=url, score=score, grade=grade,
                        issues="; ".join(issues), passed_checks="; ".join(passed_checks),
                        user_id=user_id
                    )
                    db.session.add(new_scan)
                    db.session.commit()
            except Exception as db_err:
                logger.error("DB commit failed: %s", db_err)
                db.session.rollback()
            return {"task_id": task_id, "url": url, "score": score, "grade": grade, "issues": issues, "passed_checks": passed_checks}
        else:
            issues.append(f"Header check failed: {err_msg}")
            score -= 20
    else:
        score += header_res.get("score_delta", 0)
        for h, data in header_res.get("checks", {}).items():
            if data["present"]:
                passed_checks.append(f"Header present: {h}")
            else:
                issues.append(f"Missing header: {h}")

    # 2. SSL/TLS Analysis
    ssl_res = check_ssl(url)
    if ssl_res["ok"]:
        score += ssl_res.get("score_delta", 0)
        if ssl_res.get("valid"):
            passed_checks.append(f"SSL Certificate Valid ({ssl_res.get('days_left')} days left)")
        else:
            issues.append("SSL Certificate Invalid or Expired")
            
        if ssl_res.get("cipher_strength") == "Strong":
            passed_checks.append(f"Strong SSL/TLS Cipher Suite: {ssl_res.get('cipher')}")
        else:
            issues.append(f"Weak SSL/TLS Cipher Suite detected: {ssl_res.get('cipher')}")
    else:
        issues.append(f"SSL check failed: {ssl_res.get('error', 'Unknown')}")
        score += ssl_res.get("score_delta", -30)

    # 3. CMS Detection
    cms_res = detect_cms(url)
    if cms_res["ok"]:
        score += cms_res.get("score_delta", 0)
        for issue in cms_res.get("issues", []):
            issues.append(issue)
        if cms_res.get("cms", {}).get("generator"):
             passed_checks.append(f"CMS Detected: {cms_res['cms']['generator']}")
    else:
         issues.append(f"CMS detection failed: {cms_res.get('error', 'Unknown')}")

    if score > 100: score = 100
    if score < 0: score = 0

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 50:
        grade = "C"
    elif score >= 25:
        grade = "D"
    else:
        grade = "F"

    try:
        with app.app_context():
            scan = ScanResult(
                task_id=task_id,
                url=url,
                score=score,
                grade=grade,
                issues="; ".join(issues),
                passed_checks="; ".join(passed_checks),
                user_id=user_id
            )
            db.session.add(scan)
            db.session.commit()
            logger.info("Saved scan id=%s task_id=%s url=%s", scan.id, task_id, url)
    except Exception as e:
        logger.exception("Failed to save scan result for task_id=%s url=%s: %s", task_id, url, e)

    return {"task_id": task_id, "url": url, "score": score, "grade": grade, "issues": issues, "passed_checks": passed_checks}
