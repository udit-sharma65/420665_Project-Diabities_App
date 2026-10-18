import re

from flask_wtf import FlaskForm
from sqlalchemy import func, select
from wtforms import BooleanField, FloatField, PasswordField, SelectField, StringField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Regexp,
    ValidationError,
)

from .extensions import db
from .models import User
from .services.predictor import SMOKING_LABELS, get_metadata, numeric_ranges

RANGES = numeric_ranges()
META = get_metadata()
YES_NO = [(0, "No"), (1, "Yes")]


def strong_password(form, field):
    value = field.data or ""
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one letter and one number.")


def range_field(label, key):
    low, high = RANGES[key]
    return FloatField(
        label,
        validators=[
            InputRequired(message="This field is required."),
            NumberRange(min=low, max=high, message=f"Value must be between {low:g} and {high:g}."),
        ],
        render_kw={"type": "number", "step": "any", "min": low, "max": high},
    )


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(r"^[A-Za-z0-9_]+$", message="Use letters, numbers and underscores only."),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=128), strong_password]
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )

    def validate_username(self, field):
        exists = db.session.scalar(
            select(User).where(func.lower(User.username) == field.data.strip().lower())
        )
        if exists:
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        exists = db.session.scalar(
            select(User).where(User.email == field.data.strip().lower())
        )
        if exists:
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")


class PredictionForm(FlaskForm):
    gender = SelectField(
        "Gender",
        choices=[(g, g) for g in META["categorical_values"]["gender"]],
        validators=[DataRequired()],
    )
    age = range_field("Age (years)", "age")
    hypertension = SelectField("Hypertension", choices=YES_NO, coerce=int)
    heart_disease = SelectField("Heart disease", choices=YES_NO, coerce=int)
    smoking_history = SelectField(
        "Smoking history",
        choices=[
            (s, SMOKING_LABELS.get(s, s)) for s in META["categorical_values"]["smoking_history"]
        ],
        validators=[DataRequired()],
    )
    bmi = range_field("BMI (kg/m²)", "bmi")
    hba1c_level = range_field("HbA1c level (%)", "HbA1c_level")
    blood_glucose_level = range_field("Blood glucose level (mg/dL)", "blood_glucose_level")
