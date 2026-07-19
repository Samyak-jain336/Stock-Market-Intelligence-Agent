from typing import TypedDict, Optional
import pandas as pd
from langgraph.graph import StateGraph, END

# Import the nodes
from agent.nodes import (
    detect_language,
    translate_question,
    validate_question,
    generate_sql,
    validate_sql,
    execute_sql,
    validate_results,
    write_insight,
    translate_output,
    text_to_speech,
    handle_error
)

# Define AgentState
class AgentState(TypedDict):
    question: str
    sql: Optional[str]
    valid_question: Optional[bool]
    valid: Optional[bool]
    error: Optional[str]
    results: Optional[pd.DataFrame]
    execution_error: Optional[str]
    valid_results: Optional[bool]
    insight: Optional[str]
    attempts: int
    language: Optional[str]
    audio_path: Optional[str]

# Routing functions
def route_validate_question(state: AgentState) -> str:
    if state.get("valid_question") is False:
        return END
    return "generate_sql"

def route_validate_sql(state: AgentState) -> str:
    valid = state.get("valid")
    attempts = state.get("attempts", 0)
    if valid is False:
        if attempts < 2:
            return "generate_sql"
        else:
            return "handle_error"
    return "execute_sql"

def route_execute_sql(state: AgentState) -> str:
    execution_error = state.get("execution_error")
    attempts = state.get("attempts", 0)
    if execution_error is not None:
        if attempts < 2:
            return "generate_sql"
        else:
            return "handle_error"
    return "validate_results"

def route_validate_results(state: AgentState) -> str:
    valid_results = state.get("valid_results")
    if valid_results is False:
        return "handle_error"
    return "write_insight"

def build_graph():
    # Create the StateGraph
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("detect_language", detect_language)
    workflow.add_node("translate_question", translate_question)
    workflow.add_node("validate_question", validate_question)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("validate_results", validate_results)
    workflow.add_node("write_insight", write_insight)
    workflow.add_node("translate_output", translate_output)
    workflow.add_node("text_to_speech", text_to_speech)
    workflow.add_node("handle_error", handle_error)

    # Set entry point
    workflow.set_entry_point("detect_language")

    # Edges for entry/translation/validation
    workflow.add_edge("detect_language", "translate_question")
    workflow.add_edge("translate_question", "validate_question")

    # Add conditional edges
    workflow.add_conditional_edges(
        "validate_question",
        route_validate_question,
        {
            END: END,
            "generate_sql": "generate_sql"
        }
    )

    # Normal edge
    workflow.add_edge("generate_sql", "validate_sql")

    workflow.add_conditional_edges(
        "validate_sql",
        route_validate_sql,
        {
            "generate_sql": "generate_sql",
            "handle_error": "handle_error",
            "execute_sql": "execute_sql"
        }
    )

    workflow.add_conditional_edges(
        "execute_sql",
        route_execute_sql,
        {
            "generate_sql": "generate_sql",
            "handle_error": "handle_error",
            "validate_results": "validate_results"
        }
    )

    workflow.add_conditional_edges(
        "validate_results",
        route_validate_results,
        {
            "handle_error": "handle_error",
            "write_insight": "write_insight"
        }
    )

    # Final normal edges
    workflow.add_edge("write_insight", "translate_output")
    workflow.add_edge("translate_output", "text_to_speech")
    workflow.add_edge("text_to_speech", END)
    workflow.add_edge("handle_error", END)

    # Compile the graph
    return workflow.compile()
