import datetime 
import json
import math
import os
import random
import string
import models # registers the models with Base.metadata
import redis
import time

from fastapi import FastAPI, Request, status, HTTPException # type: ignore
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models import clicks, urls

from schemas import Body
from database import Base, engine
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url, decode_responses=True)

REFILL_RATE = 5 #1 token per 5 seconds
BUCKET_CAPACITY = 10 #10 tokens maximum 

# print("creating table")
Base.metadata.create_all(engine) # generate schema

@app.get("/{code}/stats")
async def getStats(code : str, req : Request):

    key = f"rate-limit:{req.client.host}"
    
    await checkLimit(key)

    now = datetime.today()
    last_24_hours = now - timedelta(days=1)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    
    with Session(engine) as session:

        query = select(
            func.count().label("clicks_lifetime"),
            func.count().filter(clicks.timestamp >= last_24_hours).label("clicks_last_24hrs"),
            func.count().filter(clicks.timestamp >= last_7_days).label("clicks_last_7days"),
            func.count().filter(clicks.timestamp >= last_30_days).label("clicks_last_30days"),
        ).where(clicks.short_code == code)

        result = session.execute(query).one()

    statistics = {
        "lifetime_clicks": result.clicks_lifetime,
        "clicks_24_hrs": result.clicks_last_24hrs,
        "clicks_7_days": result.clicks_last_7days,
        "clicks_30_days": result.clicks_last_30days
    }

    return statistics

@app.get("/{code}")
async def getLink(code : str, req : Request):

    key = f"rate-limit:{req.client.host}"

    await checkLimit(key)

    session = Session(engine)    

    query = select(urls.original_url).where(urls.short_code == code)

    url = session.execute(query).scalar_one_or_none()

    if url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    
    with session:
        
        click_data = clicks(
            short_code = code,
            ip_address = req.client.host,
            user_agent = req.headers.get("user-agent")
        )

        session.add(click_data)

        session.commit()

    
    return RedirectResponse(
        url=url,
        status_code=status.HTTP_301_MOVED_PERMANENTLY
    )

@app.post("/shorten")
async def shorten(body : Body, req : Request):

    key = f"rate-limit:{req.client.host}"

    await checkLimit(key)
    
    return await postUrl(str(body.url), req)

# "/shorten" endpoint logic
async def postUrl(original_url : str, req : Request):
    
    with Session(engine) as session:
        result = session.scalar(select(urls).where(urls.original_url == original_url))

        if result is not None:

            click = clicks(
                short_code = result.short_code,
                ip_address = req.client.host,
                user_agent = req.headers.get("user-agent")
            )

            session.add(click)
            session.commit()

            return result.short_code
        else:
            shortened_url =  "".join(random.choices(string.ascii_letters + string.digits, k = 6))

            result = session.scalar(select(urls.short_code).where(urls.short_code == shortened_url))

            while (result is not None):
                shortened_url =  "".join(random.choices(string.ascii_letters + string.digits, k = 6))
                result = session.scalar(select(urls.short_code).where(urls.short_code == shortened_url))

            link = urls(
                short_code = shortened_url,
                original_url = original_url
            )

            session.add(link)

            session.commit()

            return shortened_url

# Token bucket rate limiter
async def checkLimit(key : str):
    # Get previous request timestamp and token amount
    timestamp_prev = r.hget(key, "timestamp")
    tokens_prev = r.hget(key, "tokens")

    now = time.time()

    # If user IP address not in redis cache add and use one token
    if tokens_prev is None:
        r.hset(
                key, 
                mapping = {
                    "tokens": BUCKET_CAPACITY - 1,
                    "timestamp": now
                }
        )
    # Otherwise calculate available tokens, tokens refilled, and consume one token
    else:
        tokens_prev = float(tokens_prev)
        timestamp_prev = float(timestamp_prev)
        
        time_elapsed = now - timestamp_prev

        tokens_curr = min(tokens_prev + time_elapsed / REFILL_RATE, 
                        BUCKET_CAPACITY)
        
        # Not enough tokens available for request, limit and return 429 error
        if (tokens_curr < 1):
            r.hset(key,
                mapping={
                    "tokens": tokens_curr,
                    "timestamp": now
                })
        
            raise HTTPException(status_code=429, detail="Rate limit exceeded, please wait")
        else:
            tokens_curr -= 1

            r.hset(key,
                mapping={
                    "tokens": tokens_curr,
                    "timestamp": now
                })    


