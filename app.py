from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import os
import re
from prompts import SYS_PROMPT
import requests
from pydantic import BaseModel, Field

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage

memory = SqliteSaver.from_conn_string(":memory:")

model_name = "moonshotai/kimi-k2.6"


class AgentState(TypedDict):
    pro:str
    con:str
    content:List[str]
    pro_search_topics:List[str]
    con_search_topics:List[str]

class Procon(BaseModel):
    """ The prompts to generate the for(pro) argument and against(con) argument  """
    pro:str = Field(description="the prompt for the pro argument")
    pro_search_topics: List[str] = Field(description="the search topics for the pro argument")
    con:str = Field(description="the prompt for the con argument")
    con_search_topics: List[str] = Field(description="the search topics for the con argument")

model = ChatOpenRouter(
    model = model_name,
    temperature = 0.1,
    max_retries = 1
)









messages=[
    SystemMessage(content=SYS_PROMPT)
]

response1 = model.with_structured_output(Procon).invoke(messages)
print(response1.pro,"\n","*"*20,"\n","*"*20,"\n",response1.con,"\n","*"*20,"\n","*"*20,"\n",response1.pro_search_topics,"\n","*"*20,"\n","*"*20,"\n",response1.con_search_topics)
