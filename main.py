import os
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx

app = FastAPI()

# In-memory storage (simulate DB for demo purposes)
duve_reservation_details: Dict[str, Dict[str, Any]] = {}
smoobu_reservations: Dict[str, Dict[str, Any]] = {}

DUVE_HOOK_URL = "https://connect.duve.com/api/v1/hooks/duveconnect?pid=6856e4877bd2d41f36a42210"
DUVE_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImNvbXBhbnkiOiI1ZTJjNmQwNzk0ODQ2MTBjNDcxMTIwYmIiLCJjb25uZWN0aW9uIjoiNjg1NmU0ODc3YmQyZDQxZjM2YTQyMjEwIiwiYWRkaXRpb25hbEZpZWxkcyI6WyJhbXlmaW5laG91c2VfYm9va2luZ19kYXRlX0ZwbmQyelVkM0wiXX0sImlzcyI6IkR1dmUiLCJqdGkiOiJ2NThHa25EaHoifQ.lkLhikJYtO13qcMq-AZF9CnBHhTWx2xl9KcpdtI5fxo"  # Replace with your actual Duve token


class DuveHookPayload(BaseModel):
    accountId: str
    event: str
    resource: Dict[str, Any]


class WebhookPayload(BaseModel):
    action: str
    user: int
    data: Any


@app.post("/duve/webhook")
async def receive_duve_webhook(payload: DuveHookPayload):

    print(f"Received DUVE WEBHOOK - {payload}")

    external_id = payload.resource.get("externalId")
    reservation_id = payload.resource.get("id")

    if not external_id:
        return {"error": "externalId missing from Duve payload"}
    
    if not reservation_id:
        return {"error": "reservationId missing from Duve payload"}
    
    duve_reservation_details[external_id] = payload.resource
    print("--about to forward from DUVE")
    await try_forward_combined_data(external_id)
    return {"status": "Duve data received"}


@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    print(f"Received {payload.action} from user {payload.user}")
    print(payload.data)

    # You can implement custom logic here:
    # if payload.action == "updateRates":
    #     handle_rate_update(payload.user, payload.data)
    if payload.action == "newReservation":
        # handle_new_reservation(payload.user, payload.data)
        external_id = str(payload.data.get("id"))
        smoobu_reservations[external_id] = payload.data
        print("--about to forward from SMOOBU")
        await try_forward_combined_data(external_id)
    # elif payload.action == "cancelReservation":
    #     handle_cancel_reservation(payload.user, payload.data)
    # elif payload.action == "updateReservation":
    #     handle_update_reservation(payload.user, payload.data)

    return {"status": "Smoobu data received"}


async def try_forward_combined_data(external_id: str):
    duve_data = duve_reservation_details.get(external_id)
    smoobu_data = smoobu_reservations.get(external_id)

    print(f"duve dataaaaa: {duve_data}")

    print(f"smoobu dataaaaa: {smoobu_data}")
    
    if duve_data and smoobu_data:
        # Both hooks received, extract and send to Duve
        created_at = smoobu_data.get("created-at")
        if not created_at:
            return  # Don't send if incomplete
        
        reservation_id = duve_data.get("id")
        if not reservation_id:
            return  # Don't send if incomplete

        duve_payload = {
            "externalReservation": external_id,
            "reservation": reservation_id,
            "additionalFields": [
                {
                    "name": "amyfinehouse_booking_date_Fpnd2zUd3L",
                    "value": f"{created_at}"
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {DUVE_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        print("*******")
        print(duve_payload)

        async with httpx.AsyncClient() as client:
            response = await client.post(DUVE_HOOK_URL, json=duve_payload, headers=headers)
            print(f"Sent to Duve: {response.status_code} - {response.text}")

        # Optional: Clean up memory
        del duve_reservation_details[external_id]
        del smoobu_reservations[external_id]


# def handle_rate_update(user_id, data):
#     print(f"Updating rates for all user {user_id}: {data}")

# def handle_new_reservation(user_id, data):
#     print(f"New reservation for user {user_id}: {data}")

# def handle_cancel_reservation(user_id, data):
#     print(f"Cancel reservation for user {user_id}: {data}")

# def handle_update_reservation(user_id, data):
#     print(f"Update reservation for user {user_id}: {data}")
