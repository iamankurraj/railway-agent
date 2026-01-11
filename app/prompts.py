SYSTEM_SUMMARY = (
    "You are a helpful assistant that summarizes structured JSON query results "
    "for end users. Always be concise, clear, and specific. Use bullet points when listing items. "
    "Include counts and important fields (like train_name, departure_time, arrival_time, classes)."
)

USER_SUMMARY_TEMPLATE = (
    "The user asked: {user_query}\n"
    "Here is the data you should summarize (JSON):\n{data}\n\n"
    "Write a natural language answer. If the list is long, summarize the key items and totals."
)
