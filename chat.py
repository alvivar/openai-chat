import argparse
import json
import os

import openai
import pyperclip  # type: ignore
from colorama import Fore  # type: ignore


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
KEYS_PATH = os.path.join(BASE_PATH, "keys.txt")
CONVERSATION_PATH = os.path.join(BASE_PATH, "conversation.json")

ENGINE = {"gpt4": "gpt-4", "gpt3.5": "gpt-3.5-turbo"}
KEYWORDS = ["as an ai", "as an artificial", "as a language"]


def load_environment_keys():
    with open(KEYS_PATH, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

def read_file_or_default(filename, default):
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return " ".join(file.read().split())
    else:
        return default

def clean_conversation(conversation):
    return [
        x for x in conversation
        if x["role"] != "assistant" or not any(k in x["content"].lower() for k in KEYWORDS)
    ]


def openai_initialize():
    openai.organization = os.environ["OPENAI_ORGANIZATION"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

def openai_response(engine, conversation):
    return openai.ChatCompletion.create(
        model=engine,
        messages=conversation,
        max_tokens=1024,
        temperature=1
    )

def input_you():
    return input(f"{Fore.YELLOW}\n\nYou: ")

def print_you(content):
    print(f"{Fore.YELLOW}\n\nYou: {content}")

def print_assistant(content):
    print(f"{Fore.BLUE}\n\n{content}")


def main(args):
    load_environment_keys()
    openai_initialize()

    system_content = read_file_or_default(" ".join(args.prompt_file), "Consider previous conversations in your answers. Don't complain.")
    engine = ENGINE["gpt4"] if args.gpt4 else ENGINE["gpt3.5"]

    print(f"{Fore.MAGENTA}\nchat.py")
    print(f"{engine.upper()}: {system_content}")

    conversation = []
    if not args.clean and os.path.isfile(CONVERSATION_PATH):
        with open(CONVERSATION_PATH, "r", encoding="utf-8") as file:
            conversation = json.load(file)
    conversation = [msg for msg in conversation if msg["role"] != "system"]
    conversation = clean_conversation(conversation)
    conversation.append({"role": "system", "content": system_content})

    for msg in conversation:
        if msg["role"] == "user":
            print_you(f"{msg['content']}")
        elif msg["role"] == "assistant":
            print_assistant(f"{msg['content']}")

    while True:
        user_input = input_you()

        if len(conversation) >= 10:
            conversation = [msg for msg in conversation if msg["role"] != "system"]
            conversation = conversation[-10:]
            conversation.insert(0, {"role": "system", "content": system_content})
        conversation = clean_conversation(conversation)
        conversation.append({"role": "user", "content": user_input})

        response = openai_response(engine, conversation)
        assistant_reply = response['choices'][0]['message']['content'].strip()
        pyperclip.copy(assistant_reply)

        print_assistant(f"{assistant_reply}")

        conversation.append({"role": "assistant", "content": assistant_reply})
        with open(CONVERSATION_PATH, "w", encoding="utf-8") as file:
            json.dump(conversation, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", nargs="*", help="System prompt file")
    parser.add_argument("--gpt4", action="store_const", const=True, help="Use GPT-4 instead of GPT-3.5 Turbo")
    parser.add_argument("--clean", action="store_const", const=True, help="Ignore previous conversations")
    args = parser.parse_args()

    main(args)
