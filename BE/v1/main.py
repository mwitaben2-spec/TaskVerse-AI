from fastapi import FastAPI
from jaclang import Jac

app = FastAPI()

# Initialize Jac runtime
jac = Jac()

# Run your Jac logic file
jac.run("main.jac")

@app.get("/")
def read_root():
    return {"message": "Jac backend is live!"}

@app.post("/run_jac")
def run_jac_logic():
    """
    Example endpoint to trigger your Jac logic from the frontend.
    Adjust this according to your Jac code.
    """
    result = jac.run("main.jac")
    return {"status": "success", "result": result}
