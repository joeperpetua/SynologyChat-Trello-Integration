from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, Union
import logging
import json
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler(sys.stdout)],
)


def handle_create():
    logging.info(f"[POST] [handle_create] --- processing")
    return


def handle_change():
    logging.info(f"[POST] [handle_change] --- processing")
    return


def handle_rename():
    logging.info(f"[POST] [handle_rename] --- processing")
    return


def handle_move():
    logging.info(f"[POST] [handle_move] --- processing")
    return


def handle_comment():
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
    logging.info(
        f"[POST] [receiverTrello] --- action ==> {action['display']['translationKey']}"
    )

    match action["display"]["translationKey"]:
        case "action_create_card":
            handle_create()
        case "action_changed_description_of_card":
            handle_change()
        case "action_renamed_card":
            handle_rename()
        case "action_moved_card_from_list_to_list":
            handle_move()
        case "action_comment_on_card":
            handle_comment()

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
