from pprint import pprint
from typing import Dict
from gidgetlab.abc import GitLabAPI


async def run_get(gl: GitLabAPI, endpoint: str, params: Dict, nb_items: int) -> None:
    """Get one or several items"""
    result = await gl.getitem(endpoint, params=params)
    if not isinstance(result, list):
        pprint(result, sort_dicts=False)
    else:
        if nb_items > 0 and len(result) >= nb_items:
            for counter, item in enumerate(result, start=1):
                if counter > nb_items:
                    break
                pprint(item, sort_dicts=False)
        else:
            counter = 1
            async for item in gl.getiter(endpoint, params=params):
                if nb_items > 0 and counter > nb_items:
                    break
                pprint(item, sort_dicts=False)
                counter += 1
    await gl._client.aclose()
