# Standard lib
import os
from typing import Dict, Any
import argparse

# 3rd party
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.llm_result import LLMResult 
from langchain_core.agents import AgentAction, AgentFinish

# Local
from chaingpt.cli.agent import ChainGPTAgent
from chaingpt.cli.display import display_tool_call, display_response
from chaingpt.utils.config import config


class ChainGPTAgentCallback(BaseCallbackHandler):
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run when chain ends running."""
        output = finish.return_values["output"]
        display_response(output)
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        display_tool_call(tool_name=action.tool, tool_input=action.tool_input)


class ChainGPTApp:
    def __init__(self, url: str):
        self.url = url
        self.agent = ChainGPTAgent(self.url)

    def chatloop(self):
        print("\nWelcome to ChainGPT! Provide a prompt or type `exit` to quit.")
        while True:
            prompt = input("Enter a prompt > ")
            if prompt == "exit":
                return
            self.agent.prompt(prompt, ChainGPTAgentCallback())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The GitHub repository URL of interest")
    args = parser.parse_args()

    app = ChainGPTApp(args.url)
    app.chatloop()
