from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import os
import re
import requests
from pydantic import BaseModel, Field

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage



class Procon(BaseModel):
    """ The prompts to generate the for(pro) argument and against(con) argument  """
    pro:str = Field(description="the prompt for the pro argument")
    con:str = Field(description="the prompt for the con argument")


memory = SqliteSaver.from_conn_string(":memory:")

model_name = "moonshotai/kimi-k2.6"


model = ChatOpenRouter(
    model = model_name,
    temperature = 0.1,
    max_retries = 1
)



SYS_PROMPT = """
For the following proposition, generate a positive prompt and a negative prompt for agents  to look into: 
Is it justified to build compromised systems now for speed or build secure systems later?
label your prompt as "PRO PROMPT:" and "CON PROMPT:"
"""

messages=[
    SystemMessage(content=SYS_PROMPT)
]

response1 = model.with_structured_output(Procon).invoke(messages)
print(response1.pro,"\n",response1.con)
