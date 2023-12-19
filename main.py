import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, Union
import requests
import logging
import json
import sys

load_dotenv()
CHAT_URL=os.getenv('SYNO_CHAT_ADDRESS')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler(sys.stdout)],
)

# logging.info(f"{CHAT_URL}")

def send_to_chat(text):
    url = "https://chat.synology.com/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=\"" + os.getenv('SYNO_CHAT_TOKEN') + "\"&payload={\"text\":\"" + text + "\"}"

    response = requests.request("GET", url)
    logging.info(f"[POST] [handle_send] --- {url} / {response.text}")


def handle_create(data, display):
    logging.info(f"[POST] [handle_create] --- processing")
    task_name = data['card']['name']
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"_Update in project board._\\n* *Action:* Task Creation.\\n* *Task list:* {task_list}\\n* *Task name:* {task_name}\\n* *Author:* {author}"

    send_to_chat(webhook_text)

    return


def handle_change(data, display):
    logging.info(f"[POST] [handle_change] --- processing")
    return


def handle_rename(data, display):
    logging.info(f"[POST] [handle_rename] --- processing")
    return


def handle_move(data, display):
    logging.info(f"[POST] [handle_move] --- processing")
    return


def handle_comment(data, display):
    logging.info(f"[POST] [handle_comment] --- processing")
    return


app = FastAPI()

# HEAD for Trello verification
@app.head("/receiverTrello")
def read_receiverTrello():
    logging.info(f"[HEAD] [receiverTrello] --- Received request.")
    return {"status": 200}

@app.post("/receiverTrello")
async def read_receiverTrello(request: Request):
    request_json = await request.json()
    logging.info(f"[POST] [receiverTrello] --- Received request ==> {request_json}")

    action = request_json.get("action", {})
    display = action['display']
    data = action['data']
    logging.info(
        f"[POST] [receiverTrello] --- action ==> {display['translationKey']}"
    )
    
    match action["display"]["translationKey"]:
        case "action_create_card":
            handle_create(data, display)
        case "action_changed_description_of_card":
            handle_change(data, display)
        case "action_renamed_card":
            handle_rename(data, display)
        case "action_move_card_from_list_to_list":
            handle_move(data, display)
        case "action_comment_on_card":
            handle_comment(data, display)

    return {"status": 200}