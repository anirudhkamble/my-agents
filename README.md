# My Agents

## Agents

1. **Gadget Shopper Agent**
AI agent to help user find electronic gadgets within certain budget. Built using langgraph, the agent has 2 nodes: First one searches for gadgets and the second provides user with gadget info. and URL(s) links where they can shop for the gadget.

2. **News Agent**
AI agent built using Google ADK provides news articles. A router agent depending upon user input invokes the correct sub-agent to provide the news related to either sports, entertainment or business.


## Setup the environment
```shell
cd news-agent
./setup.sh
```
Similary you setup the other agent(s).


## How to use the agents?
```shell
cd news-agent
python3 agents.py
```
Similary you run the other agent(s).
