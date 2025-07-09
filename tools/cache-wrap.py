#!/usr/bin/env python3 
import sys
import runpy
import requests
import requests_cache
import typer

class FullyCachedSession(requests_cache.CachedSession):
    def __init__(self, *args, **kwargs):
        super().__init__(
            cache_name=FullyCachedSession.cache_name,
            backend='filesystem',
            expire_after=None,
            serializer='json',
            allowable_methods=('DELETE', 'PUT', 'GET', 'POST'),
            ignore_cache_control=True,
            *args, **kwargs
        )

def list_cache():
    """List all cached requests with filename, body tags, and endpoint"""
    from rich import print
    from rich.panel import Panel
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
    session = FullyCachedSession()
    for key, response in session.cache.responses.items():
        print(f"[plum1]{FullyCachedSession.cache_name}/{key}.json[/] "
              f"[aquamarine1]{response.url}[/]")
        if response.request.body:
            console.print(Syntax(response.request.body.decode('utf-8'), 'json', theme='monokai', background_color="black", word_wrap=True), end=' ')
        print()

app = typer.Typer()

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    script_path: str = typer.Argument(None, help="Script to run with caching"),
    list: bool = typer.Option(False, "--list", help="List cached requests"),
    cache_dir: str = typer.Option('http_cache', "--cache-dir", help="Cache directory")
):
    """Run script with cached requests or list cached entries"""
    FullyCachedSession.cache_name = cache_dir 
    if list:
        list_cache()
        return
    if not script_path:
        ctx.get_help()
        raise typer.Exit(code=1)

    requests.Session = FullyCachedSession

    sys.argv = [script_path] + ctx.args
    runpy.run_path(script_path, run_name="__main__")

app()
