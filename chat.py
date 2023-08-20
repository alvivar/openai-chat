import argparse
import json
import os

import openai
from colorama import Fore
from pyperclip import copy


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(BASE_PATH, "keys.txt")
FULL_FILE = os.path.join(BASE_PATH, "log.full.json")
LAST_FILE = os.path.join(BASE_PATH, "log.last.json")

MAX_TOKENS = 2048
TEMPERATURE = 1
ENGINE = {"gpt4": "gpt-4", "gpt3": "gpt-3.5-turbo"}

DEFAULT_PROMPT = "Answer anything. Match the user personality."
BANNED_WORDS = [
    "as an ai",
    "as an artificial",
    "as a language",
    "can't",
    "cannot",
    "no puedo",
]


def load_environment_keys(filename):
    """
    Expecting a file named {KEYS_FILE} with content like this:

    OPENAI_ORGANIZATION=org-eXZlNW56dmt5d2Zq
    OPENAI_API_KEY=sk-YWs5aHRtbHFhdWpidWpmc3YxeTVjZXR1
    """
    with open(filename, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key.strip()] = value.strip()


def read_prompt_or(filename, default):
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            text = ""
            for line in file:
                if line.strip().startswith("#"):
                    continue
                text += line

            return " ".join(text.split())
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


def filter_unwanted(messages, keywords):
    return [
        x
        for x in messages
        if x["role"] == "user"
        or x["role"] == "assistant"
        and not any(kw in x["content"].lower() for kw in keywords)
        #  x["role"] == "system" is also expected to be removed with this logic.
    ]


def openai_initialize():
    openai.organization = os.environ["OPENAI_ORGANIZATION"]
    openai.api_key = os.environ["OPENAI_API_KEY"]


def openai_response(engine, messages):
    return openai.ChatCompletion.create(
        model=engine, messages=messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE
    )


def main(args):
    load_environment_keys(KEYS_FILE)
    openai_initialize()

    system_content = read_prompt_or(" ".join(args.prompt_file), DEFAULT_PROMPT)
    engine = ENGINE["gpt4"] if args.gpt4 else ENGINE["gpt3"]

    print(f"{Fore.MAGENTA}\nchat.py powered by {engine.upper()}")
    print(f'System prompt: "{system_content}"')

    messages = []
    if not args.clean and os.path.isfile(FULL_FILE):
        messages = load_json(FULL_FILE)

    for msg in messages[-10:]:  # @todo Make it an argument?
        if msg["role"] == "user":
            print_you(f"{msg['content']}")
        elif msg["role"] == "assistant":
            print_assistant(f"{msg['content']}")

    while True:
        user_input = input_you()

        messages.append({"role": "user", "content": user_input})

        # I'm filtering when the assistante don't want to answer to avoid
        # sending garbage back to OpenAI. The role system is also removed to
        # keep it fresh by adding it again at the top.
        # @todo Make it an argument.
        filtered = filter_unwanted(messages, BANNED_WORDS)[-4:]
        filtered.insert(0, {"role": "system", "content": system_content})

        dump_json(LAST_FILE, filtered)

        response = openai_response(engine, filtered)
        assistant_reply = response["choices"][0]["message"]["content"].strip()
        copy(assistant_reply)
        messages.append({"role": "assistant", "content": assistant_reply})

        dump_json(FULL_FILE, messages)

        print_assistant(f"{assistant_reply}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", nargs="*", help="System prompt file")
    parser.add_argument(
        "--gpt4",
        action="store_const",
        const=True,
        help="Use GPT-4 instead of GPT-3.5 Turbo",
    )
    parser.add_argument(
        "--clean", action="store_const", const=True, help="Ignore previous messages"
    )
    args = parser.parse_args()

    main(args)
