from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {"FastAPI": "Desde Docker en Python"}

