import argparse
import json
import os

import openai
import pyperclip  # type: ignore
from colorama import Fore  # type: ignore


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
KEYS_PATH = os.path.join(BASE_PATH, "keys.txt")
CHAT_PATH = os.path.join(BASE_PATH, "log.full.json")
LAST_PATH = os.path.join(BASE_PATH, "log.last.json")

ENGINE = {"gpt4": "gpt-4", "gpt3.5": "gpt-3.5-turbo"}
KEYWORDS = ["as an ai", "as an artificial", "as a language", "can't", "cannot"]
DEFAULT_PROMPT = "Consider previous chats in your answers. Match the user personality. Don't complain."


def load_environment_keys():
    """
    Expecting a file with content like this:

    OPENAI_ORGANIZATION=org-aQ975daacbuA9nbD
    OPENAI_API_KEY=sk-jOaNijiBAR1lWV9pKn6IuB8MIHT0p38R
    """
    with open(KEYS_PATH, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

def read_prompt_or(filename, default):
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return " ".join(file.read().split())
    else:
        return default

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []

def dump_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)

def input_you():
    return input(f"{Fore.YELLOW}\n\nYou: ")

def print_you(content):
    print(f"{Fore.YELLOW}\n\nYou: {content}")

def print_assistant(content):
    print(f"{Fore.BLUE}\n\n{content}")

def filter_unwanted(chat):
    return [
        x for x in chat
        if x["role"] == "user" or
           x["role"] == "assistant" and not any(k in x["content"].lower() for k in KEYWORDS)
    ]

def openai_initialize():
    openai.organization = os.environ["OPENAI_ORGANIZATION"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

def openai_response(engine, chat):
    return openai.ChatCompletion.create(
        model=engine,
        messages=chat,
        max_tokens=1024,
        temperature=1
    )


def main(args):
    load_environment_keys()
    openai_initialize()

    system_content = read_prompt_or(" ".join(args.prompt_file), DEFAULT_PROMPT)
    engine = ENGINE["gpt4"] if args.gpt4 else ENGINE["gpt3.5"]

    print(f"{Fore.MAGENTA}\nchat.py powered by {engine.upper()}")
    print(f"System prompt: \"{system_content}\"")

    chat = []
    if not args.clean and os.path.isfile(CHAT_PATH):
        chat = load_json(CHAT_PATH)

    for msg in chat[-10:]:
        if msg["role"] == "user":
            print_you(f"{msg['content']}")
        elif msg["role"] == "assistant":
            print_assistant(f"{msg['content']}")

    while True:
        user_input = input_you()

        chat.append({"role": "user", "content": user_input})
        filtered_chat = filter_unwanted(chat)[-4:]
        filtered_chat.insert(0, {"role": "system", "content": system_content})

        dump_json(LAST_PATH, filtered_chat)

        response = openai_response(engine, filtered_chat)
        assistant_reply = response['choices'][0]['message']['content'].strip()
        pyperclip.copy(assistant_reply)
        chat.append({"role": "assistant", "content": assistant_reply})

        dump_json(CHAT_PATH, chat)

        if any(k in assistant_reply.lower() for k in KEYWORDS):
            assistant_reply = "..."

        print_assistant(f"{assistant_reply}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", nargs="*", help="System prompt file")
    parser.add_argument("--gpt4", action="store_const", const=True, help="Use GPT-4 instead of GPT-3.5 Turbo")
    parser.add_argument("--clean", action="store_const", const=True, help="Ignore previous chats")
    args = parser.parse_args()

    main(args)
