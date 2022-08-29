from typing import Tuple
import re

DICT_COMMAND_WITH_ARGS = {"add": "add",
                          "change": "change",
                          "phone": "phone",
                          "birthday": "birthday",
                          "delete": "delete",
                          "find": "find"}

DICT_COMMAND_NO_ARGS = {"hello": "hello",
                        "exit": "exit",
                        "close": "exit",
                        "good bye": "exit",
                        "show all": "show_all"}

KEYWORDS_pattern = r"|".join(DICT_COMMAND_WITH_ARGS.keys())


def parse_user_input(user_input: str):
    user_input = user_input.strip()
    user_input_lower = user_input.lower()
    command = ""
    args = ""
    if user_input_lower in DICT_COMMAND_NO_ARGS.keys():
        command = DICT_COMMAND_NO_ARGS[user_input_lower]
    else:
        result = re.match(KEYWORDS_pattern, user_input_lower)
        if result:
            command = result.group()
            args = user_input[result.end():].strip()

    return command, args


def get_phone_from_args(args: str) -> str:

    phone = ""
    phone_pattern = r"\+?\d+\(?\d+\)?\d+\-?\d+\-?\d+"
    result = re.search(phone_pattern, args)
    if result:
        phone = result.group()

    return phone


def get_email_from_args(args: str) -> str:

    email = ""
    email_pattern = r"\w+@\w+\.\w{2,}"
    result = re.search(email_pattern, args)
    if result:
        email = result.group()

    return email


def get_birthday_from_args(args: str) -> str:

    birthday = ""
    birthday_pattern = r"\d{2}\-\d{2}\-\d{4}"
    result = re.search(birthday_pattern, args)
    if result:
        birthday = result.group()

    return birthday
