from fastapi import FastAPI
from scrapers import ScraperPutLockers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    locker_scraper = ScraperPutLockers("")
    return locker_scraper.scrape_main()


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
