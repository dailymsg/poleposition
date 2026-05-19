def build_system_prompt(topic: str) -> str:
    normalized_topic = topic.strip().lower().replace("-", "_")

    if normalized_topic == "support_reply":
        return (
            "You write concise customer support replies. "
            "Acknowledge the issue, ask for any missing detail, and avoid "
            "promising refunds or account changes."
        )

    if normalized_topic == "product_explainer":
        return (
            "Explain the product idea in clear, practical language for a "
            "non-technical stakeholder."
        )

    if normalized_topic == "release_notes":
        return (
            "Write concise release notes. Group changes by user-facing impact "
            "and avoid internal implementation details."
        )

    return "Be clear, accurate, and concise while staying on topic."
