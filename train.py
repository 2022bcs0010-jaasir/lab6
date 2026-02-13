import os
import json
import pickle
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


print("Name: Mohamed Jaasir Subair")
print("Roll no: 2022BCS0010")

os.makedirs("output/model", exist_ok=True)
os.makedirs("app/artifacts", exist_ok=True)


df = pd.read_csv("dataset/winequality-red.csv", sep=";")

X = df.drop("quality", axis=1)
y = df["quality"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42)

model = RandomForestRegressor(
    n_estimators=80, max_depth=15, random_state=42)

model.fit(X_train, y_train)

pred = model.predict(X_test)

mse_exp06 = mean_squared_error(y_test, pred)
r2_exp06 = r2_score(y_test, pred)
print("RF-01 MSE:", mse_exp06)
print("RF-01 R2 :", r2_exp06)








with open("output/model/trained_model.pkl", "wb") as f:
    pickle.dump(model, f)

metrics = {
    "MSE": mse_exp06,
    "R2": r2_exp06
}

with open("app/artifacts/metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)
