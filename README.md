# chat.py

A simple continuous chat with OpenAI GPT3 and GPT4.

And some additional prompt files.

```
usage: chat.py [-h] [--gpt4] [--clean] [prompt_file ...]

positional arguments:
prompt_file  System prompt file

options:
-h, --help   show this help message and exit
--gpt4       Use GPT-4 instead of GPT-3.5 Turbo
--clean      Ignore previous messages
```

## Auth

-   Expects a file named **keys.txt** where every line becomes an environmental
    variable.

```
OPENAI_ORGANIZATION=org-YVE5NzVkYWFjYnVB
OPENAI_API_KEY=sk-ak9hTmlqaUJBUjFsV1Y5cEtuNkl1QjhN
```

## To do

-   Separate different conversations into different logs.
-   Include an argument to represent the number of previous messages sent to provide more context.
-   Handle OpenAI API errors.
-   Support other engines through an argument.
