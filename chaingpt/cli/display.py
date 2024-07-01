# Standard lib
from typing import Dict

# 3rd party
from colorama import Fore, Style
from emoji import emojize


def _display_file_qa(tool_input: str):
    print(emojize(":page_facing_up: " + Fore.BLUE + "Analyzing " + Fore.YELLOW + tool_input["file_path"] + Fore.BLUE + ": " + Fore.YELLOW + tool_input["question"]))
    print(Style.RESET_ALL, end="")


def _display_search_path(tool_input: str):
    print(emojize(":magnifying_glass_tilted_left: " + Fore.BLUE + "Searching paths matching " + Fore.YELLOW + tool_input["path"]))
    print(Style.RESET_ALL, end="")



def _display_run_script(tool_input: str):
    deps_list = tool_input["deps"].replace(" ", "").split(",")
    deps = f"{Fore.BLUE}, {Fore.YELLOW}".join(deps_list)
    print(emojize(":robot: " + Fore.BLUE + "With " + Fore.YELLOW + deps + Fore.BLUE + " executing " + Fore.YELLOW + tool_input["script"]))
    print(Style.RESET_ALL, end="")



def _display_wolfi_search(tool_input: str):
    print(emojize(":magnifying_glass_tilted_left: " + Fore.BLUE + "Searching Wolfi for " + Fore.YELLOW + tool_input["keywords"]))
    print(Style.RESET_ALL, end="")


# TODO: There is a better way to design the tool calls to scale
def display_tool_call(tool_name: str, tool_input: Dict[str, str]):
    if tool_name == "file_qa":
        _display_file_qa(tool_input)
    elif tool_name == "search_path":
        _display_search_path(tool_input)
    elif tool_name == "run_script":
        _display_run_script(tool_input)
    elif tool_name == "wolfi_search":
        _display_wolfi_search(tool_input)
    else:
        # TODO: Implement an unknown tool case
        pass


def display_response(response: str):
    print(Fore.GREEN + response)
    print(Style.RESET_ALL, end="")