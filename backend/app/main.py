from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "ResumeIQ API is running"
    }