from fastapi import FastAPI

app = FastAPI(title="VetLink API")

@app.get("/")
def read_root():
    return {"message": "Welcome to VetLink API 🐾"}
