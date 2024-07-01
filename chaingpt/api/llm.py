# Standard lib
from operator import itemgetter
from dataclasses import dataclass

# 3rd party
from tqdm import tqdm
import openai
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback

# Local
from chaingpt.utils import config


openai.api_key = config.config["secrets"]["openai_api_key"]
LLM_MODEL = config.config["llm"]["file_qa_model"]


# Used to summarize of file chunk
summarize_chunk_prompt = """
    You are scanning the contents of a large file from a GitHub repository
    located at the path {file_path}. You are analyzing the file chunk by chunk in order
    to answer the question '{question}'. You have created the the following running summary
    from the previous chunks:

    <summary>
    {summary}
    </summary>


    Update this summary using information from the chunk provided below. Only include information
    relevant to the query. Respond with only the resulting summary. If the chunk contains no
    relevant information, respond with only the unmodified summary.

    <chunk>
    {chunk}
    </chunk>
    """

# Used to answer the final question for the summary constructed over chunks
read_summary_prompt = """
    You are scanning the contents of a large file from a GitHub repository located at
    the path {file_path}. You scanned the file chunk by chunk, summarizing each chunk
    for information to answer the question '{question}'. A summary of the information from these
    chunks is given below. Using this summary, answer the provided question. If the summaries do
    not contain information relevant to the question, reply that there is not enough information
    in the file to provide an answer.

    <summary>
    {summary}
    </summary>
    """

llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

summarize_chunk_chain = ({
    "file_path": itemgetter("file_path"),
    "question": itemgetter("question"),
    "chunk": itemgetter("chunk"),
    "summary": itemgetter("summary")}
    | PromptTemplate.from_template(summarize_chunk_prompt)
    | llm
    | StrOutputParser()
)

read_summary_chain = ({
    "file_path": itemgetter("file_path"),
    "question": itemgetter("question"),
    "summary": itemgetter("summary")}
    | PromptTemplate.from_template(read_summary_prompt)
    | llm
    | StrOutputParser()
)


@dataclass
class LLMResponse():
    """
    A object representing the response from a LLM.

    output (str): The raw string output.
    model (str): The model used.
    input_tokens (str): The number of input tokens sent.
    output_tokens (str): The number of output token generated.
    """
    output: str
    model: str
    input_tokens: int
    output_tokens: int


def text_qa_map_reduce(question: str, text: str,
                       file_path: str="unknown",
                       chunk_size: int=10000,
                       chunk_overlap: int=500) -> LLMResponse:
    """
    Uses an LLM to analyze a body of text according to a question. Text
    is split into chunks and analyzed using in-place map reduce.

    Args:
        question (str): The question to ask.
        text (str): The text to analyze.
        file_path (str, optional): The file path that the text originates from. Provides the LLM with additional context.
        chunk_size (int, optional): The chunk size to use when splitting the text.
        chunk_overlap (int, optional): The size of the overlap between chunks.
    
    Returns:
        An `LLMResponse` object containing the response from the LLM.
    
    Raises:
        ValueError: If the `chunk_size` is not smaller than the length of `text`.
    """
    if len(text) <= chunk_size:
        raise ValueError(f"The length of `text` must be greater than `chunk_size`. {len(text)} is not > {chunk_size}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)
    docs = splitter.split_text(text)
    
    with get_openai_callback() as cb:
        summary = "[No summary (This is the first chunk) - Replace me]"
        for doc in tqdm(docs, desc="Processing large file in chunks"):
            inputs = {
                "file_path": file_path,
                "question": question,
                "chunk": doc,
                "summary": summary
            }
            summary = summarize_chunk_chain.invoke(inputs)
    
        output = read_summary_chain.invoke({
            "file_path": file_path,
            "question": question,
            "summary": summary
        })

        return LLMResponse(output=output,
                           model=LLM_MODEL,
                           input_tokens=cb.prompt_tokens,
                           output_tokens=cb.completion_tokens)


"""
TODO:The following prompts and chains are akin to the above but simply stuff the entire
file into the prompt (no chunking). These prompts and chains need to be wrapped under one object
and support one OR many chunks so we don't have to manage two implementations.

TODO: Consider returning LangChain objects instead of LLMResponse
"""

qa_prompt = """
    You are scanning the contents of a file from a GitHub repository located at
    the path {file_path}. You are trying to answer the question '{question}'. Use only the provided
    content below. If the content does not contain any information relevant to the question, reply that
    there is not enough information in the file to provide an answer.

    content:

    {content}
    """


qa_chain = ({
    "file_path": itemgetter("file_path"),
    "question": itemgetter("question"),
    "content": lambda x: "\n\n".join(x["content"])}
    | PromptTemplate.from_template(qa_prompt)
    | llm
    | StrOutputParser()
)


def text_qa(question: str, text: str,
            file_path: str="unknown") -> LLMResponse:
    """
    Uses an LLM to analyze a body of text according to a question.

    Args:
        question (str): The question to ask.
        text (str): The text to analyze.
        file_path (str, optional): The file path that the text originates from. Provides the LLM with additional context.
    
    Returns:
        An `LLMResponse` object containing the response from the LLM.
    """
    inputs = {
        "file_path": file_path,
        "question": question,
        "content": text
    }

    with get_openai_callback() as cb:
        output = qa_chain.invoke(inputs)
        return LLMResponse(output=output,
                           model=LLM_MODEL,
                           input_tokens=cb.prompt_tokens,
                           output_tokens=cb.completion_tokens)
