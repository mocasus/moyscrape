import json
import click

from moyscrape.core.engine import Engine


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["eng"] = Engine()


@cli.command()
@click.argument("url")
@click.option("--format", "fmt", default="markdown",
              type=click.Choice(["markdown", "html", "json"]))
@click.option("--proxy", default=None)
@click.option("--browser", is_flag=True, help="Force Playwright render")
def scrape(url, fmt, proxy, browser):
    """Scrape a single URL."""
    eng = Engine()
    res = eng.scrape(url, fmt=fmt, proxy=proxy, force_browser=browser)
    if fmt == "json":
        click.echo(json.dumps(res, indent=2, default=str))
    else:
        click.echo(res["content"])


@cli.command()
@click.argument("url")
@click.option("--depth", default=1)
@click.option("--limit", default=20)
@click.option("--proxy", default=None)
def crawl(url, depth, limit, proxy):
    """Crawl from URL, following links."""
    eng = Engine()
    res = eng.crawl(url, depth=depth, limit=limit, proxy=proxy)
    click.echo(f"crawled {len(res)} pages")
    for r in res:
        click.echo(f"- {r['url']} ({len(r.get('content',''))} chars)")


@cli.command()
@click.argument("url")
@click.option("--depth", default=1)
@click.option("--limit", default=50)
def map(url, depth, limit):
    """Collect URLs only."""
    eng = Engine()
    for u in eng.map_urls(url, depth=depth, limit=limit):
        click.echo(u)


@cli.command()
@click.argument("url")
@click.option("--schema", default=None,
              help="Path to JSON schema file or inline JSON")
def extract(url, schema):
    """Extract structured data via LLM (needs LLM_API_KEY)."""
    eng = Engine()
    if schema and schema.strip().startswith("{"):
        sch = json.loads(schema)
    else:
        sch = json.loads(open(schema).read())
    res = eng.extract(url, sch)
    click.echo(json.dumps(res, indent=2, default=str))


@cli.command()
@click.argument("urls", nargs=-1)
def batch(urls):
    """Scrape multiple URLs."""
    eng = Engine()
    for u in urls:
        r = eng.scrape(u)
        click.echo(f"{u}: {len(r.get('content',''))} chars")


@cli.command()
def sites():
    """List registered plugins + YAML presets."""
    eng = Engine()
    click.echo("Plugins: " + ", ".join(eng.plugin_domains()) or "(none)")
    click.echo("Presets: " + ", ".join(eng.preset_domains()) or "(none)")


@cli.command()
def validate():
    """Validate all plugins + presets load."""
    eng = Engine()
    click.echo("OK" if eng.validate() else "FAILED")


if __name__ == "__main__":
    cli()
