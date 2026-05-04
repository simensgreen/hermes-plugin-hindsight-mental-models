"""Tool schemas for Hindsight mental model lookup."""

HINDSIGHT_GET_MENTAL_MODEL = {
    "name": "hindsight_get_mental_model",
    "description": (
        "Retrieve a precomputed Hindsight mental model directly by bank_id and model_id. "
        "Use this BEFORE broad hindsight_recall or hindsight_reflect when you need stable user context, "
        "such as user profile, preferences, current location/timezone, active tasks, plans, tools, "
        "infrastructure, or recurring project context. This tool returns the saved mental model content "
        "without asking Hindsight to re-analyze all memories. If this lookup fails or the model is missing, "
        "then fall back to hindsight_reflect or targeted hindsight_recall."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bank_id": {
                "type": "string",
                "description": "Hindsight memory bank ID configured for your deployment.",
            },
            "model_id": {
                "type": "string",
                "description": "Mental model ID as returned by the list tool or your Hindsight setup.",
            },
            "detail": {
                "type": "string",
                "enum": ["metadata", "content", "full"],
                "description": (
                    "How much data to return. Use content for agent orientation. "
                    "Use metadata for quick checks. Avoid full unless debugging provenance."
                ),
                "default": "content",
            },
        },
        "required": ["bank_id", "model_id"],
    },
}


HINDSIGHT_LIST_MENTAL_MODELS = {
    "name": "hindsight_list_mental_models",
    "description": (
        "List Hindsight mental models in a bank. Use this when you do not know the model_id. "
        "Prefer detail=metadata for discovery, then call hindsight_get_mental_model with the chosen ID."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bank_id": {
                "type": "string",
                "description": "Hindsight memory bank ID configured for your deployment.",
            },
            "detail": {
                "type": "string",
                "enum": ["metadata", "content", "full"],
                "description": (
                    "How much data to return. Use metadata for listing IDs. "
                    "Use content only if the agent needs all model contents."
                ),
                "default": "metadata",
            },
        },
        "required": ["bank_id"],
    },
}
