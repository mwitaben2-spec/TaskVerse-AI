from fastapi import FastAPI
from jaclang import jac_import

app = FastAPI()

# Load your Jac logic
jac_import("main.jac")

@app.get("/")
def read_root():
    return {"message": "Jac backend is live!"}