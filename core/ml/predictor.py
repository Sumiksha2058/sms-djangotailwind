import joblib

model = joblib.load("ml/pass_fail_model.pkl")

def predict_pass_fail(attendance, avg_marks):
    return model.predict([[attendance, avg_marks]])[0]
