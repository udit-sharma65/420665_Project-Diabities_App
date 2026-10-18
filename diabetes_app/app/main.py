import json

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, select

from .extensions import db
from .forms import PredictionForm
from .models import Prediction
from .services.predictor import (
    get_feature_importance,
    get_metadata,
    get_model_comparison,
    predict,
)
from .services.recommender import recommend

bp = Blueprint("main", __name__)


def owned_prediction_or_404(prediction_id):
    record = db.session.get(Prediction, prediction_id)
    if record is None or record.user_id != current_user.id:
        abort(404)
    return record


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    base = select(Prediction).where(Prediction.user_id == current_user.id)
    total = db.session.scalar(
        select(func.count()).select_from(Prediction).where(Prediction.user_id == current_user.id)
    )
    recent = db.session.scalars(base.order_by(Prediction.created_at.desc()).limit(5)).all()
    latest = recent[0] if recent else None
    return render_template("dashboard.html", total=total, latest=latest, recent=recent)


@bp.route("/predict", methods=["GET", "POST"])
@login_required
def predict_view():
    form = PredictionForm()
    if form.validate_on_submit():
        values = {
            "gender": form.gender.data,
            "age": float(form.age.data),
            "hypertension": form.hypertension.data,
            "heart_disease": form.heart_disease.data,
            "smoking_history": form.smoking_history.data,
            "bmi": float(form.bmi.data),
            "HbA1c_level": float(form.hba1c_level.data),
            "blood_glucose_level": float(form.blood_glucose_level.data),
        }
        outcome = predict(values)
        recommendations = recommend(values, outcome["risk_level"])
        record = Prediction(
            user_id=current_user.id,
            gender=values["gender"],
            age=values["age"],
            hypertension=values["hypertension"],
            heart_disease=values["heart_disease"],
            smoking_history=values["smoking_history"],
            bmi=values["bmi"],
            hba1c_level=values["HbA1c_level"],
            blood_glucose_level=values["blood_glucose_level"],
            risk_probability=outcome["probability"],
            risk_level=outcome["risk_level"],
            predicted_class=outcome["predicted_class"],
            recommendations=json.dumps(recommendations),
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("main.result", prediction_id=record.id))
    return render_template("predict.html", form=form)


@bp.route("/result/<int:prediction_id>")
@login_required
def result(prediction_id):
    record = owned_prediction_or_404(prediction_id)
    return render_template("result.html", record=record, meta=get_metadata())


@bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    query = (
        select(Prediction)
        .where(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
    )
    pagination = db.paginate(
        query,
        page=page,
        per_page=current_app.config["HISTORY_PER_PAGE"],
        error_out=False,
    )
    return render_template("history.html", pagination=pagination)


@bp.route("/history/<int:prediction_id>/delete", methods=["POST"])
@login_required
def delete_prediction(prediction_id):
    record = owned_prediction_or_404(prediction_id)
    db.session.delete(record)
    db.session.commit()
    flash("Assessment deleted.", "info")
    return redirect(url_for("main.history"))


@bp.route("/about")
def about():
    return render_template(
        "about.html",
        meta=get_metadata(),
        comparison=get_model_comparison(),
        importance=get_feature_importance(),
    )
