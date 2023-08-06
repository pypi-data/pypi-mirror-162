from typing import Tuple


def create_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Created {resource_type} '{name}'",)


def would_create_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Would create {resource_type} '{name}'",)


def update_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Updated {resource_type} '{name}'",)


def would_update_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Would update {resource_type} '{name}'",)


def delete_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Deleted {resource_type} '{name}'",)


def would_delete_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"Would delete {resource_type} '{name}'",)


def already_absent_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"{resource_type} '{name}' already absent",)


def already_exists_comment(hub, resource_type: str, name: str) -> Tuple:
    return (f"{resource_type} '{name}' already exists",)


def update_tags_comment(hub, tags_to_remove, tags_to_add) -> Tuple:
    return (
        f"Update tags: Add keys {tags_to_add.keys()} Remove keys {tags_to_remove.keys()}",
    )


def would_update_tags_comment(hub, tags_to_remove, tags_to_add) -> Tuple:
    return (
        f"Would update tags: Add keys {tags_to_add.keys()} Remove keys {tags_to_remove.keys()}",
    )


def get_empty_comment(hub, resource_type: str, name: str) -> str:
    return f"Get {resource_type} '{name}' result is empty"


def list_empty_comment(hub, resource_type: str, name: str) -> str:
    return f"List {resource_type} '{name}' result is empty"


def find_more_than_one(hub, resource_type: str, resource_id: str) -> str:
    return (
        f"More than one {resource_type} resource was found. Use resource {resource_id}"
    )


def resource_status_updated_comment(
    hub, resource_type: str, name: str, new_status: str
) -> str:
    return (
        f"The status of the {resource_type} with name - {name} is updated to {new_status}",
    )
