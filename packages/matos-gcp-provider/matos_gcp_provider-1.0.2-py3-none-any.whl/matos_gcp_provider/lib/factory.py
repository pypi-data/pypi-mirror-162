from typing import Any, Dict

_PLUGINS: Dict[str, Any] = {}


def register(resource_type: str, creator_fn: Any) -> None:
    """Register a new resource type."""
    _PLUGINS[resource_type] = creator_fn


def fetch_plugins() -> Dict[str, Any]:
    return _PLUGINS


def create(arguments: Dict[str, Any]) -> Any:
    """Create a resource of a specific type, given JSON data."""
    args_copy = arguments.copy()
    resource_type = args_copy.get("type")
    try:
        creator_func = _PLUGINS[resource_type]
    except KeyError:
        raise ValueError(f"unknown resource type {resource_type!r}") from None
    return creator_func(args_copy)
