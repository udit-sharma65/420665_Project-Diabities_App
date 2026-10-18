# DiabetesCheck

A Flask web application that estimates diabetes risk from a user's health details using a machine learning model trained in Google Colab. Users register and log in, submit an assessment, receive a risk level with tailored recommendations, and keep a private history. Data is stored in SQLite. There is no admin role.

> Academic screening tool built on an anonymised public dataset. It is not a medical diagnosis.

## Features

- Register, log in and log out (passwords hashed, CSRF protection, per-user data isolation)
- Health assessment form with server-side range validation and a built-in BMI calculator
- Calibrated SVM model returns a probability and a Low, Moderate or High risk level
- Rule-based recommendations grouped into medical follow-up, readings, lifestyle and monitoring
- Assessment history with pagination and delete
- About page showing model metrics, model comparison and feature importance
- Automated tests with pytest

## Tech stack

Python 3.10 to 3.12, Flask, Flask-SQLAlchemy (SQLite), Flask-Login, Flask-WTF, scikit-learn 1.6.1, pandas, Bootstrap 5 (loaded from a CDN, so an internet connection is needed for styling).

## Project structure

```
diabetes_app/
├── run.py                       entry point
├── config.py                    settings (SECRET_KEY, database, test config)
├── requirements.txt
├── .env.example                 copy to .env
├── app/
│   ├── __init__.py              application factory
│   ├── extensions.py
│   ├── models.py                User and Prediction tables
│   ├── forms.py                 registration, login and assessment forms
│   ├── auth.py                  register, login, logout
│   ├── main.py                  dashboard, predict, result, history, about
│   ├── services/
│   │   ├── predictor.py         loads the model and returns risk
│   │   └── recommender.py       recommendation rules
│   ├── model/                   diabetes_model.pkl, model_metadata.json, CSV tables
│   ├── templates/
│   └── static/
├── notebooks/Diabetes_Prediction_Analysis.ipynb
├── tests/
└── .vscode/                     launch and test settings
```

## Setup in VS Code

### 1. Prerequisites

- [Python 3.10, 3.11 or 3.12](https://www.python.org/downloads/) (tick "Add Python to PATH" on Windows). scikit-learn 1.6.1 does not yet install on Python 3.14.
- [Visual Studio Code](https://code.visualstudio.com/) with the **Python** extension (Microsoft).

Check your Python version in a terminal:

```
python --version
```

On macOS or Linux use `python3` in place of `python` if needed.

### 2. Open the project

1. Unzip `diabetes_app.zip`.
2. In VS Code choose **File > Open Folder** and select the `diabetes_app` folder.
3. Open the integrated terminal with **Terminal > New Terminal**. The prompt should be inside `diabetes_app`.

### 3. Create and activate a virtual environment

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again. In Command Prompt use `.venv\Scripts\activate.bat`.

macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

The terminal prompt now starts with `(.venv)`.

### 4. Select the interpreter

Press `Ctrl+Shift+P` (`Cmd+Shift+P` on macOS), choose **Python: Select Interpreter** and pick the one inside `.venv`. If VS Code offers to use the new environment when it detects it, accept.

### 5. Install the dependencies

```
pip install -r requirements.txt
```

### 6. Configure the environment (optional but recommended)

Copy `.env.example` to `.env` and replace the secret key with a long random string:

```
SECRET_KEY=your-long-random-string
```

Generate one with:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

The app also runs without a `.env` file by using a development key.

### 7. Run the application

```
python run.py
```

Open http://127.0.0.1:5000 in your browser.

To run with the VS Code debugger instead, open **Run and Debug** (`Ctrl+Shift+D`), select **Flask: run app** and press `F5`.

The SQLite database is created automatically at `instance/app.db` on the first run.

### 8. Use the app

1. Click **Register** and create an account.
2. Log in.
3. Open **New assessment**, fill in the form and submit.
4. Review the risk level and recommendations, then find past results under **History**.

Example values that give a low result: Female, age 25, no hypertension, no heart disease, never smoked, BMI 22, HbA1c 4.8, glucose 90. Values that give a high result: Male, age 65, hypertension and heart disease, former smoker, BMI 34, HbA1c 7.5, glucose 220.

## Running the tests

```
pytest
```

The tests cover registration and login rules, protected routes, prediction for low and high risk, input validation, per-user data isolation, deletion and the recommendation rules. They can also be run from the VS Code **Testing** panel.

## Model files

The application loads two files from `app/model/`:

| File | Purpose |
|---|---|
| `diabetes_model.pkl` | Full scikit-learn pipeline (scaler, encoder and calibrated linear SVM) |
| `model_metadata.json` | Feature order, allowed values, input ranges, risk bands, metrics |

`model_comparison.csv` and `feature_importance.csv` feed the About page.

To use a newer model, rerun the notebook in `notebooks/`, then replace these four files with the ones it exports. Keep the installed scikit-learn version equal to the `sklearn_version` stored in `model_metadata.json` (currently 1.6.1).

## Risk levels

Risk levels come from the predicted probability using the bands in `model_metadata.json`: Low below 30%, Moderate from 30% to below 60%, High from 60%. The model classification shown on the result page uses the 50% decision threshold.

## Troubleshooting

| Problem | Fix |
|---|---|
| `No matching distribution found for scikit-learn==1.6.1` | Use Python 3.10 to 3.12 and recreate the virtual environment |
| `InconsistentVersionWarning` or the model fails to load | Run `pip install scikit-learn==1.6.1` |
| `ModuleNotFoundError` | Activate `.venv` and run `pip install -r requirements.txt` again |
| Port 5000 already in use | Stop the other process, or run `flask --app run run --port 5001` |
| Page looks unstyled | Bootstrap loads from a CDN, so check your internet connection |
| Want a clean database | Stop the app and delete the `instance/` folder |
| Session errors after changing `SECRET_KEY` | Log in again |

## Security notes

- Passwords are stored as salted hashes, never in plain text.
- Every form is protected by CSRF tokens, and logout and delete are POST-only.
- Each user can only open or delete their own assessments.
- Database access goes through SQLAlchemy, which prevents SQL injection.
- Set a strong `SECRET_KEY` and run behind a production server with HTTPS (not `python run.py`) if you ever deploy this.
