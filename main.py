from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any

app = FastAPI()

class WebhookPayload(BaseModel):
    action: str
    user: int
    data: Any

@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    print(f"Received {payload.action} from user {payload.user}")
    print(payload.data)

    # You can implement custom logic here:
    if payload.action == "updateRates":
        handle_rate_update(payload.user, payload.data)
    elif payload.action == "newReservation":
        handle_new_reservation(payload.user, payload.data)
    elif payload.action == "cancelReservation":
        handle_cancel_reservation(payload.user, payload.data)
    elif payload.action == "updateReservation":
        handle_update_reservation(payload.user, payload.data)

    return {"status": "received"}

def handle_rate_update(user_id, data):
    print(f"Updating rates for all user {user_id}: {data}")

def handle_new_reservation(user_id, data):
    print(f"New reservation for user {user_id}: {data}")

def handle_cancel_reservation(user_id, data):
    print(f"Cancel reservation for user {user_id}: {data}")

def handle_update_reservation(user_id, data):
    print(f"Update reservation for user {user_id}: {data}")
