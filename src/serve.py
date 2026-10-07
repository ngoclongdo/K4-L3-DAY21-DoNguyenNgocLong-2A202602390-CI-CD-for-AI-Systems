from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu S3 bucket ve may khi server khoi dong.
    Su dung AWS credentials/IAM role tren EC2 hoac bien moi truong.
    """
    # TODO 1: Tao s3 client
    s3 = boto3.client("s3")

    # TODO 2: Tao thu muc chua model neu chua co
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # TODO 3: Tai file model xuong may
    print(f"Dang tai model tu S3 s3://{ARTIFACT_BUCKET}/{MODEL_KEY} ve {MODEL_PATH}...")
    s3.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)

    # TODO 4: In thong bao thanh cong
    print("Model da duoc tai xuong tu cloud storage (AWS S3).")


# Chi tai khi khong trong moi truong test cuc bo (khi ARTIFACT_BUCKET ton tai)
if ARTIFACT_BUCKET and not os.path.exists(MODEL_PATH):
    download_model()

model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung:
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    if len(req.features) != 10:
        raise HTTPException(
            status_code=400,
            detail=f"Dau vao phai chua dung 10 dac trung, nhan duoc {len(req.features)}",
        )

    if model is None:
        raise HTTPException(status_code=500, detail="Model chua duoc tai.")

    pred = int(model.predict([req.features])[0])
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"

    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

