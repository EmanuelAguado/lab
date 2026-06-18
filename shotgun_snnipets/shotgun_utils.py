import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from shotgun_api3.shotgun import Shotgun

SHOTGRID_URL = "https://mondotv.shotgunstudio.com"
SHOTGRID_SCRIPT_NAME = "ShotgunHandlerBase"
SHOTGRID_API_KEY = "#ebhfcJlejfxjinlvorxmwja9"


def _instantiate_shogrid() -> Shotgun:
    return Shotgun(
        SHOTGRID_URL,
        script_name=SHOTGRID_SCRIPT_NAME,
        api_key=SHOTGRID_API_KEY,
    )


def async_find(
    entity: str,
    filters: list[list[Any]] = None,
    fields: list[str] = None,
    page_size: int = 500,
) -> list[dict[str, Any]]:
    """
    Performs asynchronous paged queries on the ShotGrid API.

    Args:
        entity (str): Entity type to query (e.g., 'Task').
        filters (list[list[Any]]): ShotGrid filter list.
        fields (list[str]): Fields to retrieve.
        page_size (int): Number of results per page.

    Returns:
        list[dict[str, Any]]: Flattened list of all retrieved results.
    """
    filters = filters or []
    fields = fields or []
    sg = _instantiate_shogrid()
    total_tasks = sg.summarize(
        entity, filters, summary_fields=[{"field": "id", "type": "count"}]
    )["summaries"]["id"]

    if total_tasks == 0:
        return []

    total_pages = -(-total_tasks // page_size)
    loop = asyncio.new_event_loop()

    async def run_task(page):
        return await loop.run_in_executor(
            None,
            lambda: _instantiate_shogrid().find(
                entity, filters, fields, page=page, limit=page_size
            ),
        )

    async def gather_task():
        return await asyncio.gather(
            *[run_task(page) for page in range(1, total_pages + 1)]
        )

    result = loop.run_until_complete(gather_task())
    loop.close()
    return [item for group in result for item in group]


if __name__ == "__main__":
    import time

    sg = _instantiate_shogrid()
    fields = list(sg.schema_field_read("Task").keys())

    start = time.perf_counter()
    sg.find("Task", [], fields)
    normal_time = time.perf_counter() - start

    start = time.perf_counter()
    async_find(
        entity="Task",
        fields=fields,
    )
    async_time = time.perf_counter() - start

    print(f"Normal find : {normal_time:.2f}s")
    print(f"Async find  : {async_time:.2f}s")
    print(f"Speedup     : {normal_time / async_time:.2f}x")
