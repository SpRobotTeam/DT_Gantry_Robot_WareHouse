from typing import Dict, Optional

from mcp.server.fastmcp import FastMCP

from wcs_runtime import VALID_ALGORITHM_MODES, WarehouseRuntime

mcp = FastMCP("gantry-wcs")
runtime = WarehouseRuntime()


@mcp.tool()
def health() -> Dict[str, object]:
    """Return runtime status and current warehouse summary."""
    return runtime.health()


@mcp.tool()
def warehouse_summary() -> Dict[str, object]:
    """Return inventory, capacity, and algorithm mode."""
    return runtime.summary()


@mcp.tool()
def reset_warehouse(container_name: Optional[str] = None) -> Dict[str, object]:
    """Reset WCS state and re-initialize default areas."""
    return runtime.reset(container_name=container_name)


@mcp.tool()
def set_algorithm_mode(mode: str) -> Dict[str, object]:
    """Set algorithm mode. Valid values: FF, AO, RL, LA, RA."""
    return runtime.set_algorithm_mode(mode=mode)


@mcp.tool()
def list_product_templates() -> Dict[str, object]:
    """List available product template names."""
    return {
        "templates": runtime.list_product_templates(),
        "valid_algorithm_modes": list(VALID_ALGORITHM_MODES),
    }


@mcp.tool()
def list_inventory(product_name: Optional[str] = None, limit: int = 100) -> Dict[str, object]:
    """List lots currently in inventory."""
    return runtime.list_inventory(product_name=product_name, limit=limit)


@mcp.tool()
def inbound(product_name: str = "default", quantity: int = 1) -> Dict[str, object]:
    """Run one or more inbound operations in simulation mode."""
    return runtime.inbound(product_name=product_name, quantity=quantity)


@mcp.tool()
def outbound(
    quantity: int = 1,
    product_name: Optional[str] = None,
    lot: Optional[str] = None,
) -> Dict[str, object]:
    """Run one or more outbound operations by product or lot."""
    return runtime.outbound(quantity=quantity, product_name=product_name, lot=lot)


if __name__ == "__main__":
    mcp.run(transport="stdio")
