from app.extensions import db
from app.models import Prediction, User
from app.services.predictor import predict
from app.services.recommender import recommend

LOW = {
    "gender": "Female",
    "age": "25",
    "hypertension": "0",
    "heart_disease": "0",
    "smoking_history": "never",
    "bmi": "22",
    "hba1c_level": "4.8",
    "blood_glucose_level": "90",
}

HIGH = {
    "gender": "Male",
    "age": "65",
    "hypertension": "1",
    "heart_disease": "1",
    "smoking_history": "former",
    "bmi": "34",
    "hba1c_level": "7.5",
    "blood_glucose_level": "220",
}


def register(client, username="alice", email="alice@example.com", password="Passw0rdX"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="alice@example.com", password="Passw0rdX"):
    return client.post(
        "/login", data={"email": email, "password": password}, follow_redirects=True
    )


def signed_in(client, username="alice", email="alice@example.com"):
    register(client, username=username, email=email)
    login(client, email=email)


def test_home_page_is_public(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"DiabetesCheck" in response.data


def test_about_page_is_public(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"Models compared" in response.data


def test_register_creates_user_with_hashed_password(client, app):
    response = register(client)
    assert b"Account created successfully" in response.data
    with app.app_context():
        user = db.session.query(User).filter_by(email="alice@example.com").one()
        assert user.password_hash != "Passw0rdX"
        assert user.check_password("Passw0rdX")


def test_duplicate_email_rejected(client):
    register(client)
    response = register(client, username="alice2")
    assert b"An account with this email already exists" in response.data


def test_duplicate_username_rejected(client):
    register(client)
    response = register(client, email="other@example.com")
    assert b"This username is already taken" in response.data


def test_weak_password_rejected(client):
    response = register(client, password="onlyletters")
    assert b"at least one letter and one number" in response.data


def test_password_mismatch_rejected(client):
    response = client.post(
        "/register",
        data={
            "username": "bob",
            "email": "bob@example.com",
            "password": "Passw0rdX",
            "confirm_password": "Different1",
        },
    )
    assert b"Passwords must match" in response.data


def test_login_success_and_wrong_password(client):
    register(client)
    bad = login(client, password="WrongPass1")
    assert b"Invalid email or password" in bad.data
    good = login(client)
    assert b"Hello, alice" in good.data


def test_logout(client):
    signed_in(client)
    response = client.post("/logout", follow_redirects=True)
    assert b"You have been logged out" in response.data
    assert client.get("/dashboard").status_code == 302


def test_protected_routes_redirect_to_login(client):
    for path in ["/dashboard", "/predict", "/history", "/result/1"]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_login_rejects_external_next_redirect(client):
    register(client)
    response = client.post(
        "/login?next=https://evil.example.com/",
        data={"email": "alice@example.com", "password": "Passw0rdX"},
    )
    assert response.status_code == 302
    assert "evil.example.com" not in response.headers["Location"]


def test_low_risk_prediction(client, app):
    signed_in(client)
    response = client.post("/predict", data=LOW, follow_redirects=True)
    assert b"Low risk" in response.data
    assert b"Recommendations" in response.data
    with app.app_context():
        record = db.session.query(Prediction).one()
        assert record.risk_level == "Low"
        assert record.predicted_class == 0


def test_high_risk_prediction(client, app):
    signed_in(client)
    response = client.post("/predict", data=HIGH, follow_redirects=True)
    assert b"High risk" in response.data
    with app.app_context():
        record = db.session.query(Prediction).one()
        assert record.risk_level == "High"
        assert record.predicted_class == 1
        assert record.risk_probability > 0.6


def test_out_of_range_values_rejected(client, app):
    signed_in(client)
    bad = dict(LOW, hba1c_level="15")
    response = client.post("/predict", data=bad)
    assert response.status_code == 200
    assert b"Value must be between" in response.data
    with app.app_context():
        assert db.session.query(Prediction).count() == 0


def test_missing_values_rejected(client, app):
    signed_in(client)
    bad = dict(LOW)
    bad.pop("bmi")
    response = client.post("/predict", data=bad)
    assert b"This field is required" in response.data
    with app.app_context():
        assert db.session.query(Prediction).count() == 0


def test_history_lists_own_predictions(client):
    signed_in(client)
    client.post("/predict", data=LOW)
    client.post("/predict", data=HIGH)
    response = client.get("/history")
    assert response.data.count(b"Open") == 2


def test_users_cannot_access_each_others_results(client):
    signed_in(client)
    client.post("/predict", data=HIGH)
    client.post("/logout")
    signed_in(client, username="bob", email="bob@example.com")
    assert client.get("/result/1").status_code == 404
    history = client.get("/history")
    assert b"No assessments saved yet" in history.data


def test_delete_only_own_prediction(client, app):
    signed_in(client)
    client.post("/predict", data=LOW)
    client.post("/logout")
    signed_in(client, username="bob", email="bob@example.com")
    assert client.post("/history/1/delete").status_code == 404
    client.post("/logout")
    login(client)
    response = client.post("/history/1/delete", follow_redirects=True)
    assert b"Assessment deleted" in response.data
    with app.app_context():
        assert db.session.query(Prediction).count() == 0


def test_predictor_risk_levels():
    low = predict(
        {
            "gender": "Female",
            "age": 25.0,
            "hypertension": 0,
            "heart_disease": 0,
            "smoking_history": "never",
            "bmi": 22.0,
            "HbA1c_level": 4.8,
            "blood_glucose_level": 90.0,
        }
    )
    high = predict(
        {
            "gender": "Male",
            "age": 65.0,
            "hypertension": 1,
            "heart_disease": 1,
            "smoking_history": "former",
            "bmi": 34.0,
            "HbA1c_level": 7.5,
            "blood_glucose_level": 220.0,
        }
    )
    assert low["risk_level"] == "Low"
    assert high["risk_level"] == "High"
    assert 0 <= low["probability"] < high["probability"] <= 1


def test_recommender_reflects_inputs():
    values = {
        "gender": "Male",
        "age": 50.0,
        "hypertension": 1,
        "heart_disease": 0,
        "smoking_history": "current",
        "bmi": 32.0,
        "HbA1c_level": 6.8,
        "blood_glucose_level": 210.0,
    }
    text = " ".join(item["text"] for item in recommend(values, "High"))
    assert "diagnose diabetes" in text
    assert "obese" in text
    assert "smoking" in text
    assert "blood pressure" in text
