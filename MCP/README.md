# MCP setup for Gantry WCS

This folder provides a minimal MCP server/client integration for the WCS project.

## Install

```bash
pip install -r MCP/requirements.txt
```

## Run MCP server (stdio transport)

```bash
python3 MCP/server.py
```

The server exposes these tools:

- `health`
- `warehouse_summary`
- `reset_warehouse`
- `set_algorithm_mode`
- `list_product_templates`
- `list_inventory`
- `inbound`
- `outbound`

## Run bundled MCP client

List tools:

```bash
python3 MCP/client.py --list-tools
```

Call a tool:

```bash
python3 MCP/client.py --tool warehouse_summary
python3 MCP/client.py --tool inbound --args '{"product_name":"01","quantity":3}'
python3 MCP/client.py --tool outbound --args '{"product_name":"01","quantity":2}'
```

## Example MCP client config snippet

```json
{
  "mcpServers": {
    "gantry-wcs": {
      "command": "python3",
      "args": ["/home/qwe/DT_Gantry_Robot_WareHouse/MCP/server.py"]
    }
  }
}
```
