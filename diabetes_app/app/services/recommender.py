def recommend(values, level):
    items = []

    def add(category, text):
        items.append({"category": category, "text": text})

    age = values["age"]
    bmi = values["bmi"]
    hba1c = values["HbA1c_level"]
    glucose = values["blood_glucose_level"]

    if level == "High":
        add(
            "Medical follow-up",
            "Your result indicates a high likelihood of diabetes. Book an appointment with a doctor soon "
            "for confirmatory laboratory tests such as fasting plasma glucose and HbA1c.",
        )
        add(
            "Medical follow-up",
            "Seek urgent medical care if you develop extreme thirst, frequent urination, unexplained "
            "weight loss, blurred vision or persistent fatigue.",
        )
    elif level == "Moderate":
        add(
            "Medical follow-up",
            "Your result indicates a moderate likelihood of diabetes. Arrange a check-up within the next "
            "few weeks and ask for a blood glucose and HbA1c test to confirm where you stand.",
        )
    else:
        add(
            "Medical follow-up",
            "Your result indicates a low likelihood of diabetes. Keep attending routine health check-ups.",
        )

    if hba1c >= 6.5:
        add(
            "Your readings",
            f"Your HbA1c of {hba1c:g}% is in the range used to diagnose diabetes. "
            "This needs to be confirmed by a doctor with a laboratory test.",
        )
    elif hba1c >= 5.7:
        add(
            "Your readings",
            f"Your HbA1c of {hba1c:g}% is in the prediabetes range (5.7% to 6.4%). "
            "Lifestyle changes at this stage can prevent progression to diabetes.",
        )

    if glucose >= 200:
        add(
            "Your readings",
            f"Your blood glucose of {glucose:g} mg/dL is at or above 200 mg/dL, "
            "a level that needs prompt medical assessment.",
        )
    elif glucose >= 140:
        add(
            "Your readings",
            f"Your blood glucose of {glucose:g} mg/dL is elevated. "
            "Ask your doctor about a repeat test taken under fasting conditions.",
        )

    if bmi >= 30:
        add(
            "Lifestyle",
            f"Your BMI of {bmi:g} is in the obese range. Losing 5% to 7% of body weight "
            "gradually can significantly reduce diabetes risk.",
        )
    elif bmi >= 25:
        add(
            "Lifestyle",
            f"Your BMI of {bmi:g} is in the overweight range. Modest, steady weight loss "
            "through diet and activity helps lower risk.",
        )
    elif bmi < 18.5:
        add(
            "Lifestyle",
            f"Your BMI of {bmi:g} is below the healthy range. Consider speaking to a doctor "
            "or dietitian about balanced nutrition.",
        )

    add(
        "Lifestyle",
        "Aim for at least 150 minutes of moderate physical activity per week, such as brisk walking or cycling.",
    )
    add(
        "Lifestyle",
        "Build meals around vegetables, whole grains, legumes and lean protein, and limit sugary drinks, "
        "sweets and highly processed foods.",
    )

    if values["smoking_history"] == "current":
        add(
            "Lifestyle",
            "Stopping smoking lowers the risk of diabetes complications and heart disease. "
            "Ask your doctor about cessation support.",
        )

    if values["hypertension"]:
        add(
            "Monitoring",
            "Keep your blood pressure under control: check it regularly, reduce salt intake and follow "
            "any prescribed treatment.",
        )
    if values["heart_disease"]:
        add(
            "Monitoring",
            "Diabetes and heart disease affect each other, so share these results with the doctor "
            "who manages your heart condition.",
        )
    if level == "Low" and age >= 35:
        add(
            "Monitoring",
            "Adults aged 35 and over are advised to have their blood glucose checked regularly, "
            "typically every three years or as your doctor recommends.",
        )
    if level != "Low":
        add(
            "Monitoring",
            "Keep a record of your blood glucose and HbA1c results so you can share them with your doctor.",
        )

    return items
