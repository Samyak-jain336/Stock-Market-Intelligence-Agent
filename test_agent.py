from agent.graph import build_graph

graph = build_graph()

question = input("Enter the Nifty50 Stock Market related question: ")

result = graph.invoke({
    "question": question,
    "sql": None,
    "valid_question": None,
    "valid": None,
    "error": None,
    "results": None,
    "execution_error": None,
    "valid_results": None,
    "insight": None,
    "attempts": 0
})

print("=== SQL ===")
print(result["sql"])
print("\n=== INSIGHT ===")
print(result["insight"])
print("\n=== DATA ===")
print(result["results"])
print("\n=== AUDIO PATH ===")
print(result["audio_path"])