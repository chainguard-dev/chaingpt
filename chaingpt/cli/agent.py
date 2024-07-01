# Standard lib
from typing import Iterator

# 3rd party
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents.agent import AgentExecutor
from langchain.agents import create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler

# Local
from chaingpt.api.llm import LLMResponse
from chaingpt.cli.tools import get_tools
from chaingpt.utils import config


# TODO: Add configs for adjusting fields such as chunk size and chunk overlap
LLM_MODEL = config.config["llm"]["agent_model"]


class ChainGPTAgent:
    def __init__(self, url: str):
        self.url = url
        self._init_agent()

    def _init_agent(self):
        def callback2(output: str):
            print(output, end="")

        tools = get_tools(self.url, callback2)
        llm = ChatOpenAI(temperature=0, model=LLM_MODEL)

        prompt = PromptTemplate.from_template("""
        As an AI expert and extremely intelligent engineering assistant focusing on the %s GitHub repository,
        your key role is to engage with engineers, offering precise and reliable
        information about repository-related issues. You are equipped with specialized
        tools for searching file names, reading files, and executing shell scripts. Your responses should be concise yet thorough,
        backed by diligent verification using these tools. You are expected to research exhaustively
        and consider multiple perspectives before finalizing an answer, demonstrating your commitment
        to accuracy and detail in engineering problem-solving. When problem-solving, follow these special instructions:
        
        1) You have an extreme "Can Do!" attitude. Try to never report an error or quit without providing the answer, especially when testing shell code.
           Instead try extremely hard to diagnose the issue and test other options until eventually you encounter a working solution. Ask, nothing of the user
           before trying to do it yourself. Only then should you report your findings.
        
        2) You should do more to verify that shell commands worked than just reading stdout and stderr. You should include verification
           commands that produce additional helpful output to ensure shell commands succeeded or to help diagnose issues.
        
        3) You may be asked to run commands that produce files in the repository. Take care that the files you produce do not clash with
           the names of other files/directories in the repo. I.e, be sure to perform adequate reconnaissance in the repository.

        {chat_history}
        Question: {input}
        {agent_scratchpad}
        """ % self.url)

        self.agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
        memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, memory=memory)


    def prompt(self, msg: str, callback: BaseCallbackHandler=None) -> Iterator[LLMResponse]:
        output = self.agent_executor.invoke({"input": msg}, config={"callbacks": [callback]})
