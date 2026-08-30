import json
import os


def add_trigger(file_path, trigger_type, trigger_name):
    with open(file_path, "r") as f:
        data = json.load(f)

    # Check if trigger already exists
    has_trigger = any(n["type"] == trigger_type for n in data["nodes"])
    if not has_trigger:
        trigger_node = {
            "parameters": {},
            "name": trigger_name,
            "type": trigger_type,
            "typeVersion": 1,
            "position": [50, 300],
        }

        # Find first node to connect to
        first_node = min(data["nodes"], key=lambda x: x.get("position", [0, 0])[0])
        first_node_name = first_node["name"]

        data["nodes"].append(trigger_node)

        # Add connection
        data["connections"].setdefault(trigger_name, {})
        data["connections"][trigger_name]["main"] = [
            [{"node": first_node_name, "type": "main", "index": 0}]
        ]

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)


add_trigger(
    "workflows/n8n/customer-notification.json",
    "n8n-nodes-base.executeWorkflowTrigger",
    "Execute Workflow Trigger",
)
add_trigger(
    "workflows/n8n/payment-verification.json",
    "n8n-nodes-base.executeWorkflowTrigger",
    "Execute Workflow Trigger",
)
add_trigger(
    "workflows/n8n/error-handler.json", "n8n-nodes-base.errorTrigger", "Error Trigger"
)
