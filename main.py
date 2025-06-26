import os
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
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


reservations = [
    {"duve_id": "6857157bdf4634cb03829355", "external_id": "101422718", "created_at": "06/21/2025"},
    {"duve_id": "685734545685c2b04e0a3cab", "external_id": "101430123", "created_at": "06/21/2025"},
    {"duve_id": "682a3ce0f785741678da2093", "external_id": None, "created_at": "05/18/2025"},
    {"duve_id": "6787cccfafffa42a14246dff", "external_id": "83993283", "created_at": "01/15/2025"},
    {"duve_id": "681e4109d1fef428f8cb240c", "external_id": "96570463", "created_at": "05/09/2025"},
    {"duve_id": "683c6368639d48aa4b0cc10b", "external_id": "99106423", "created_at": "06/01/2025"},
    {"duve_id": "682bafc44f1692af29d3fdeb", "external_id": "97724288", "created_at": "05/19/2025"},
    {"duve_id": "683f17cf8bb77682fe7cdc55", "external_id": "99383943", "created_at": "06/03/2025"},
    {"duve_id": "6822a3d8927adb334bea2cf0", "external_id": "96921428", "created_at": "05/12/2025"},
    {"duve_id": "683640534d7bc42b7a232be2", "external_id": "98638148", "created_at": "05/27/2025"},
    {"duve_id": "684aa01b968a773aca7a0bde", "external_id": "100385188", "created_at": "06/12/2025"},
    {"duve_id": "6848fc7deca7347d2de94d09", "external_id": "100239458", "created_at": "06/10/2025"},
    {"duve_id": "684a612412a3354552ca1d85", "external_id": "100361783", "created_at": "06/12/2025"},
    {"duve_id": "684babdb29e18dfbb5ea62a5", "external_id": "100471963", "created_at": "06/12/2025"},
    {"duve_id": "6855f548def2f0d71578a61b", "external_id": "101347603", "created_at": "06/20/2025"},
    {"duve_id": "6856fba0df4634cb03448cd9", "external_id": "101414633", "created_at": "06/21/2025"},
    {"duve_id": "67e3109a5458a795db422fb2", "external_id": "91716723", "created_at": "03/25/2025"},
    {"duve_id": "6843344e404712cf138f4841", "external_id": "99759898", "created_at": "06/06/2025"},
    {"duve_id": "68399285eec3a97f4f6872f8", "external_id": "98902188", "created_at": "05/30/2025"},
    {"duve_id": "66c8a4fcf9f7831bfcf64cb3", "external_id": "70170661", "created_at": "08/23/2024"},
    {"duve_id": "68543acbf57ac55a1ae43e98", "external_id": "101208373", "created_at": "06/19/2025"},
    {"duve_id": "684c78a0424e081dd291e7a4", "external_id": "100552908", "created_at": "06/13/2025"},
    {"duve_id": "684f9ee5bb807b8223b06b89", "external_id": "100775403", "created_at": "06/15/2025"},
    {"duve_id": "6858522dc2542558e193c740", "external_id": "101518248", "created_at": "06/22/2025"},
    {"duve_id": "68531685bf48221cd5bd832e", "external_id": "101118708", "created_at": "06/18/2025"},
    {"duve_id": "682a4188a02064606244f54d", "external_id": "97582713", "created_at": "05/18/2025"},
    {"duve_id": "682be16e4f1692af293af29a", "external_id": "97729258", "created_at": "05/19/2025"},
    {"duve_id": "67fea7dca73649f9783df694", "external_id": "94001994", "created_at": "04/15/2025"},
    {"duve_id": "685c5e88a2c7fc0688ef22e5", "external_id": "101898203", "created_at": "06/25/2025"},
    {"duve_id": "679ae127dcc690cd4feb0308", "external_id": "85665118", "created_at": "01/29/2025"},
    {"duve_id": "682cef923a15acd2033ea7d0", "external_id": "97840668", "created_at": "05/20/2025"},
    {"duve_id": "68445a6369ca3559655b16e0", "external_id": "99837473", "created_at": "06/07/2025"},
    {"duve_id": "68054696c94dc76c04cc69c6", "external_id": "94476914", "created_at": "04/20/2025"},
    {"duve_id": "67fc0c033da04cda625113ba", "external_id": "93766754", "created_at": "04/13/2025"},
    {"duve_id": "684f208ebf2a44cad8657048", "external_id": "100752503", "created_at": "06/15/2025"},
    {"duve_id": "68365c3d4d7bc42b7a620dde", "external_id": "98641258", "created_at": "05/27/2025"},
    {"duve_id": "681ce960fa5cf704ec973302", "external_id": "96455018", "created_at": "05/08/2025"},
    {"duve_id": "683f3c04af88ac8325a47d03", "external_id": "99402713", "created_at": "06/03/2025"},
    {"duve_id": "6840878c4bd7ee78fb6d9c26", "external_id": "99525763", "created_at": "06/04/2025"},
    {"duve_id": "67816e8ebdeb6f76bcc9f6d8", "external_id": "83423123", "created_at": "01/10/2025"},
    {"duve_id": "6825431ee235fe686d42a848", "external_id": "97166743", "created_at": "05/14/2025"},
    {"duve_id": "679282de460b8f7bf1134328", "external_id": "84950738", "created_at": "01/23/2025"},
    {"duve_id": "68411b39b8c899ef4708da34", "external_id": "99563743", "created_at": "06/04/2025"},
    {"duve_id": "6834a9d32918dc9896ef5887", "external_id": "98484618", "created_at": "05/26/2025"},
    {"duve_id": "682ff90fd85033ac2b83b550", "external_id": "98084223", "created_at": "05/22/2025"},
    {"duve_id": "66d9ea1c655a67773f9aa01b", "external_id": "71513304", "created_at": "09/05/2024"},
    {"duve_id": "6816022737874d3e69b6c415", "external_id": "95818413", "created_at": "05/03/2025"},
    {"duve_id": "685c3220a2c7fc0688843d03", "external_id": "101875383", "created_at": "06/25/2025"},
    {"duve_id": "682a649aa0206460629143ab", "external_id": "97593268", "created_at": "05/18/2025"},
    {"duve_id": "6858bdeba0d75a8551c6ca9d", "external_id": "101544833", "created_at": "06/22/2025"},
    {"duve_id": "683a9a7658a24ea567163f21", "external_id": "98971003", "created_at": "05/31/2025"},
    {"duve_id": "684e00b613b8be16eeb16843", "external_id": "100659103", "created_at": "06/14/2025"}
]


@app.post("/updates")
async def send_updates():
    async with httpx.AsyncClient() as client:
        for item in reservations:
            duve_id = item["duve_id"]
            external_id = item["external_id"]
            created_at = item["created_at"]

            if not external_id:
                print(f"Skipping {duve_id}: no external_id")
                continue

            duve_payload = {
                "externalReservation": external_id,
                "reservation": duve_id,
                "additionalFields": [
                    {
                        "name": "amyfinehouse_booking_date_Fpnd2zUd3L",
                        "value": created_at
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {DUVE_BEARER_TOKEN}",
                "Content-Type": "application/json"
            }

            try:
                response = await client.post(DUVE_HOOK_URL, json=duve_payload, headers=headers)
                print(f"[{duve_id}] Sent to Duve: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[{duve_id}] Error sending to Duve: {e}")

            await asyncio.sleep(10)  # Delay 10 seconds between requests


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
