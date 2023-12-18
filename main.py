import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, Union
import logging
import json
import sys

load_dotenv()
CHAT_URL=f"https://{os.getenv('SYNO_CHAT_ADDRESS')}/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token='{os.getenv('SYNO_CHAT_TOKEN')}'"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler(sys.stdout)],
)

logging.info(f"{CHAT_URL}")

def handle_create(data, display):
    logging.info(f"[POST] [handle_create] --- processing")
    task_name = data['card']['name']
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"Update in project board.\n Action: Task Creation.\nTask list: {task_list}\nTask name: {task_name}\nAuthor: {author}"
    logging.info(f"[POST] [handle_create] --- {webhook_text}")
    return


def handle_change(data):
    logging.info(f"[POST] [handle_change] --- processing")
    return


def handle_rename(data):
    logging.info(f"[POST] [handle_rename] --- processing")
    return


def handle_move(data):
    logging.info(f"[POST] [handle_move] --- processing")
    return


def handle_comment(data):
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


    card_name = action["data"]["card"]["name"]

    if "list" in action["data"]:  # card was created / modified
        list_name = action["data"]["list"]
        if "desc" in action["data"]["card"]:
            card_desc = action["data"]["card"]["desc"]
            if card_desc == "":
                logging.info(f"Received card without description. Ignore it.")
                return {"status": 200}
            else:
                logging.info(
                    f"Task modified. Task list: {list_name} / Task name: {card_name} / Task description: {card_desc}"
                )
        else:
            logging.info(
                f"Task created. Task list: {list_name} / Task name: {card_name}"
            )

    if "listBefore" in action["data"]:  # card was moved
        previous_list = action["data"]["listBefore"]["name"]
        current_list = action["data"]["listAfter"]["name"]

        logging.info(
            f"Task moved from {previous_list} to {current_list}. Task name: {card_name}"
        )

    return {"status": 200}


""" 
Board callback
"""
# @app.post("/receiverTrello")
# async def read_receiverTrello(request: Request):
#     request_json = await request.json()
#     logging.info(f"[POST] [receiverTrello] --- Received request ==> {request_json}")

#     actions = request_json.get('action', {})
#     logging.info(f"[POST] [receiverTrello] --- action ==> {actions['display']['translationKey']}")

#     card_name = actions['data']['card']['name']


#     if 'list' in actions['data']: # card was created / modified
#         list_name = actions['data']['list']
#         if 'desc' in actions['data']['card']:
#             card_desc = actions['data']['card']['desc']
#             if card_desc == '':
#                 logging.info(f"Received card without description. Ignore it.")
#                 return {"status": 200}
#             else:
#                 logging.info(f"Task modified. Task list: {list_name} / Task name: {card_name} / Task description: {card_desc}")
#         else:
#                 logging.info(f"Task created. Task list: {list_name} / Task name: {card_name}")

#     if 'listBefore' in actions['data']: # card was moved
#         previous_list = actions['data']['listBefore']['name']
#         current_list = actions['data']['listAfter']['name']

#         logging.info(f"Task moved from {previous_list} to {current_list}. Task name: {card_name}")

#     return {"status": 200}
