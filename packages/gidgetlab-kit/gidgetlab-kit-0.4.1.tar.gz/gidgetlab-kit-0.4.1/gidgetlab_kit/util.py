from typing import Dict, List
import asyncio
import shlex
import typer


async def run_subprocess(cmd: str, cwd=None) -> str:
    """Run the command as subprocess"""
    typer.secho(f"Run {cmd}", fg=typer.colors.CYAN)
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, cwd=cwd
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip()


def convert_params_to_dict(params: List[str]) -> Dict:
    """Convert a list of key-value pairs to a dict"""
    d = {}
    for kv in params:
        if "=" not in kv:
            raise ValueError(f"Key value pair '{kv}' shall be separated by '='")
        key, _, value = kv.partition("=")
        d[key] = value
    return d
