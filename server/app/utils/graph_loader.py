"""Loads LangGraph graphs from Agentic_wf.

Keeps ALL coupling between `app/` and `Agentic_wf/` in one place. If a graph fails
to import or build, the API still boots and the dependent endpoints return 503.
"""
import importlib
import inspect
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Only used when no explicit factory name is given.
FALLBACK_FACTORY_NAMES = (
    "build_graph", "create_graph", "build_workflow", "get_graph", "build", "create_workflow",
)


def load_graph(module_path: str, factory: str | None = None, checkpointer: Any | None = None) -> Any | None:
    try:
        module = importlib.import_module(module_path)
    except Exception:
        logger.exception("Could not import graph module %s", module_path)
        return None

    names = (factory,) if factory else FALLBACK_FACTORY_NAMES
    for name in names:
        factory_fn = getattr(module, name, None)
        if factory_fn is None:
            continue
        try:
            if callable(factory_fn):
                params = inspect.signature(factory_fn).parameters
                accepts_cp = "checkpointer" in params or any(
                    p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()
                )
                if checkpointer is not None and accepts_cp:
                    result = factory_fn(checkpointer=checkpointer)
                else:
                    if checkpointer is not None:
                        logger.warning(
                            "%s.%s does not accept `checkpointer`; interrupt/resume will not work "
                            "unless it compiles with one", module_path, name,
                        )
                    result = factory_fn()
            else:
                result = factory_fn
            # An uncompiled StateGraph -> compile it (with the checkpointer if we have one)
            if not hasattr(result, "ainvoke") and hasattr(result, "compile"):
                result = result.compile(checkpointer=checkpointer) if checkpointer else result.compile()
            logger.info("Loaded graph %s.%s", module_path, name)
            return result
        except Exception:
            logger.exception("Graph factory %s.%s failed", module_path, name)
            return None

    logger.error("No graph factory found in %s (tried %s)", module_path, names)
    return None