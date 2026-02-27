import argparse
import asyncio
import json
import os
import shlex
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _model_to_plain(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _model_to_plain(value.model_dump())
    if isinstance(value, dict):
        return {key: _model_to_plain(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_model_to_plain(item) for item in value]
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MCP stdio client for Gantry WCS.")
    default_server_cmd = "{0} {1}".format(
        sys.executable, os.path.join(os.path.dirname(__file__), "server.py")
    )
    parser.add_argument(
        "--server-cmd",
        default=default_server_cmd,
        help="Server start command. Example: 'python3 MCP/server.py'",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List server tools and exit.",
    )
    parser.add_argument("--tool", help="Tool name to call.")
    parser.add_argument(
        "--args",
        default="{}",
        help='JSON args for --tool. Example: \'{"product_name":"01","quantity":2}\'',
    )
    return parser


async def _run() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    command_parts = shlex.split(args.server_cmd)
    if not command_parts:
        parser.error("--server-cmd is empty")

    params = StdioServerParameters(
        command=command_parts[0],
        args=command_parts[1:],
        env=os.environ.copy(),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            if args.list_tools or not args.tool:
                tools = await session.list_tools()
                tool_payload = [
                    {"name": tool.name, "description": tool.description} for tool in tools.tools
                ]
                print(json.dumps(tool_payload, ensure_ascii=False, indent=2))
                if not args.tool:
                    return 0

            try:
                payload = json.loads(args.args)
                if not isinstance(payload, dict):
                    raise ValueError("Tool args JSON must decode to an object.")
            except Exception as exc:
                parser.error("Invalid --args JSON: {0}".format(exc))

            result = await session.call_tool(args.tool, payload)
            print(json.dumps(_model_to_plain(result), ensure_ascii=False, indent=2))
            return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_run()))
