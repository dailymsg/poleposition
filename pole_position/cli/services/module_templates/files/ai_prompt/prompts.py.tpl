def build_system_prompt(topic: str) -> str:
    normalized_topic = topic.strip().lower().replace("-", "_")

    if normalized_topic == "product_explainer":
        return "Explain the topic in clear, non-technical language."

    if normalized_topic == "support_reply":
        return "Draft a concise, professional customer support response."

    if normalized_topic == "release_notes":
        return "Write concise release notes that highlight user-facing changes."

    return "Be clear, accurate, and concise while staying on topic."
