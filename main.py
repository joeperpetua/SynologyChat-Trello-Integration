import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, Union
import requests
import logging
import sys
import time
import re

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

def get_ctime():
    ctime = time.localtime()
    ctime_format = time.strftime("%m/%d/%Y - [%H:%M:%S]", ctime)

    # logging.info(f"[POST] [get_ctime] --- current time ==> {ctime_format}")
    return ctime_format

def convert_md_url_to_chat(text):
    # Regular expression to find and replace markdown hyperlink syntax in the original string with chat ULR format
    pattern = r'\[(.*?)\]\((https?://[^\s]+)\s*(".*")?\)'
    formatted_text = re.sub(pattern, r'<\2|\1>', text)

    logging.info(f"[POST] [convert_md_url_to_chat] --- {formatted_text}")
    return formatted_text

def handle_create(data, display):
    logging.info(f"[POST] [handle_create] --- processing")
    task_name = data['card']['name']
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"🕛 {get_ctime()}\\n🟢 *_Update in project board._*\\n✏️ *Action:* Task was created.\\n📂 *Status:* {task_list}\\n🏷️ *Task name:* {task_name}\\n💬 *Author:* {author}\\n__________________________________________________"

    send_to_chat(webhook_text)
    return


def handle_change(data, display):
    logging.info(f"[POST] [handle_change] --- processing")
    task_name = data['card']['name']
    task_desc = convert_md_url_to_chat(data['card']['desc'])
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"🕛 {get_ctime()}\\n🟢 *_Update in project board._*\\n✏️ *Action:* Task description updated..\\n📂 *Status:* {task_list}\\n🏷️ *Task name:* {task_name}\\n💡 *Task description:*\\n```{task_desc}```\\n💬 *Author:* {author}\\n__________________________________________________"

    send_to_chat(webhook_text)
    return


def handle_rename(data, display):
    logging.info(f"[POST] [handle_rename] --- processing")
    old_task_name = data['old']['name']
    task_name = data['card']['name']
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"🕛 {get_ctime()}\\n🟢 *_Update in project board._*\\n✏️ *Action:* Task name changed from _{old_task_name}_ to _{task_name}_\\n📂 *Status:* {task_list}\\n💬 *Author:* {author}\\n__________________________________________________"

    send_to_chat(webhook_text)
    return


def handle_move(model, data, display):
    logging.info(f"[POST] [handle_move] --- processing")
    model_name = model['name']
    task_name = data['card']['name']
    old_task_list = data['listBefore']['name']
    task_list = data['listAfter']['name']
    author = display['entities']['memberCreator']['text']

    # check for duplicated event
    if model_name != task_list:
        return

    webhook_text = f"🕛 {get_ctime()}\\n🟢 *_Update in project board._*\\n✏️ *Action:* Task moved from _{old_task_list}_ to _{task_list}_\\n📂 *Status:* {task_list}\\n🏷️ *Task name:* {task_name}\\n💬 *Author:* {author}\\n__________________________________________________"

    send_to_chat(webhook_text)
    return


def handle_comment(data, display):
    logging.info(f"[POST] [handle_comment] --- processing")
    task_name = data['card']['name']
    task_comment = convert_md_url_to_chat(data['text'])
    task_list = data['list']['name']
    author = display['entities']['memberCreator']['text']

    webhook_text = f"🕛 {get_ctime()}\\n🟢 *_Update in project board._*\\n✏️ *Action:* Comment added on task.\\n📂 *Status:* {task_list}\\n🏷️ *Task name:* {task_name}\\n💡 *Task comment:* \\n>{task_comment}\\n💬 *Author:* {author}\\n__________________________________________________"

    send_to_chat(webhook_text)
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

    model = request_json.get("model", {})
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
            handle_move(model, data, display)
        case "action_comment_on_card":
            handle_comment(data, display)

    return {"status": 200}