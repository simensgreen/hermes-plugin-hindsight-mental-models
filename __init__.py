"""Hindsight mental models plugin."""

from . import schemas, tools


def register(ctx):
    """Register Hindsight mental model tools."""
    ctx.register_tool(
        name="hindsight_get_mental_model",
        schema=schemas.HINDSIGHT_GET_MENTAL_MODEL,
        handler=tools.hindsight_get_mental_model,
        toolset="hindsight_mental_models",
    )
    ctx.register_tool(
        name="hindsight_list_mental_models",
        schema=schemas.HINDSIGHT_LIST_MENTAL_MODELS,
        handler=tools.hindsight_list_mental_models,
        toolset="hindsight_mental_models",
    )
