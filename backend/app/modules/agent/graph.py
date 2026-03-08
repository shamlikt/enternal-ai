"""LangGraph ReAct agent for natural language to SQL queries."""
import json
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    sql_generated: str | None
    query_results: list[dict[str, Any]] | None
    execute_fn: Any  # callable for query execution


def create_agent_graph(llm, schema_context: str):
    """Create a LangGraph ReAct agent that generates and executes SQL."""

    SYSTEM_PROMPT = f"""You are a healthcare data analyst assistant for the PCORnet CDM v7.0 data platform.
You help users query patient data using natural language questions.

Available PCORnet CDM tables and schema:
{schema_context}

Rules:
1. Only generate SELECT queries. Never generate INSERT, UPDATE, DELETE, DROP, or other DDL/DML.
2. Always use fully qualified column names to avoid ambiguity.
3. Limit results to 1000 rows by default unless asked for more.
4. Be concise and explain what the query does.

When you have a query ready, call the execute_sql tool.
"""

    @tool
    def execute_sql(sql: str) -> str:
        """Execute a SQL SELECT query against the PCORnet CDM database. Returns JSON results."""
        return f"SQL_EXECUTE:{sql}"

    llm_with_tools = llm.bind_tools([execute_sql])

    def call_model(state: AgentState) -> AgentState:
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "execute"
        return END

    def execute_tools(state: AgentState) -> AgentState:
        last_message = state["messages"][-1]
        tool_messages = []
        sql_generated = None
        query_results = None

        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "execute_sql":
                sql = tool_call["args"]["sql"]
                sql_generated = sql
                execute_fn = state.get("execute_fn")
                if execute_fn:
                    import asyncio
                    try:
                        results = asyncio.get_event_loop().run_until_complete(execute_fn(sql))
                        query_results = results
                        result_str = json.dumps(results[:50], default=str)
                        tool_content = f"Query executed successfully. {len(results)} rows returned. First 50: {result_str}"
                    except Exception as e:
                        tool_content = f"Query failed: {str(e)}"
                else:
                    tool_content = "Query execution not available"

                tool_messages.append(
                    ToolMessage(content=tool_content, tool_call_id=tool_call["id"])
                )

        return {
            "messages": tool_messages,
            "sql_generated": sql_generated,
            "query_results": query_results,
        }

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("execute", execute_tools)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("execute", "agent")

    return graph.compile()
