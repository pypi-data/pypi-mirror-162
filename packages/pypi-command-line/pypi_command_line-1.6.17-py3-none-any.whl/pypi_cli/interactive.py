import rich
import json
import datetime
from urllib.parse import quote

import humanize
import textual
import requests

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich_rst import RestructuredText


base_url = "https://pypi.org/pypi"
package_name = "rich"
version = None
console = Console()
session = requests.Session()

if not version and "==" in package_name:
    package_name, _, version = package_name.partition("==")
url = f"{base_url}/pypi/{quote(package_name)}{f'/{quote(version)}' if version else ''}/json"
with console.status("Getting data from PyPI"):
    response = session.get(url)

if response.status_code != 200:
    if response.status_code == 404:
        rich.print(f"[red]:no_entry_sign: Project [green]{package_name}[/] not found[/]")
    rich.print(f"[orange]:grey_exclamation: Some error occured. response code {response.status_code}[/]")
    raise typer.Exit()

parsed_data = json.loads(response.text)

info = parsed_data["info"]
releases = parsed_data["releases"]
urls = parsed_data["urls"]

try:
    from packaging.version import parse as parse_version  # pylint:disable=import-outside-toplevel
except ImportError:
    from distutils.version import LooseVersion as parse_version  # pylint:disable=import-outside-toplevel

from datetime import timezone  # pylint: disable=import-outside-toplevel

if urls:
    # HACK: should use fromisotime
    release_time = utc_to_local(
        datetime.strptime(urls[-1]["upload_time_iso_8601"], "%Y-%m-%dT%H:%M:%S.%fZ"), timezone.utc
    )
    natural_time = release_time.strftime("%b %d, %Y")
else:
    natural_time = "UNKNOWN"
description = info["summary"]
latest_version = list(sorted(map(parse_version, releases.keys()), reverse=True))[0]
version_comment = (
    "[green]Latest Version[/]"
    if str(latest_version) == str(info["version"])
    else f"[red]Newer version available ({latest_version})[/]"
)
import re  # pylint: disable=import-outside-toplevel

repos = re.findall(
    r"https://(?:www\.)?github\.com/(?P<repo>[A-Za-z0-9_.-]{0,38}/[A-Za-z0-9_.-]{0,100})(?:\.git)?", str(info)
)
if len(repos) > 1:
    repos = list(
        set(
            re.findall(
                r"https://(?:www\.)?github\.com/(?P<repo>[A-Za-z0-9_.-]{0,38}/[A-Za-z0-9_.-]{0,100})(?:\.git)?",
                str(info["project_urls"]),
            )
        )
    )
repo = remove_dot_git(repos[0]) if repos else None

from rich.text import Text  # pylint:disable=import-outside-toplevel

title = Text.from_markup(f"[bold cyan]{info['name']} {info['version']}[/]\n{description}", justify="left")
message = Text.from_markup(f"{version_comment}\nReleased: {natural_time}", justify="right")
table = Table.grid(expand=True)
table.add_column(justify="left")
table.add_column(justify="right")
table.add_row(title, message)

metadata = Table.grid()
metadata.add_column(justify="left")
if info.get("project_urls") and not hide_project_urls:
    metadata.add_row(
        Panel(
            "\n".join(f"[yellow]{name}[/]: [cyan]{url}[/]" for name, url in info["project_urls"].items()),
            expand=False,
            border_style="magenta",
            title="Project URLs",
        )
    )

if repo:
    url = f"https://api.github.com/repos/{quote(repo)}"
    with console.status("Getting data from GitHub"):
        resp = session.get(url)
    github_data = json.loads(resp.text)
    if github_data.get("message") and github_data["message"] == "Not Found":
        metadata.add_row(
            Panel(
                f"[red underline]Repo Not Found[/]\n[cyan]Link[/]: {url}\n[light_green]Name[/]: {repo}\n",
                expand=False,
                border_style="green",
                title="GitHub",
            )
        )
    else:
        size = github_data["size"]
        stars = github_data["stargazers_count"]
        forks = github_data["forks_count"]
        issues = github_data["open_issues"]
        metadata.add_row(
            Panel(
                f"[light_green]Name[/]: [link=https://github.com/{repo}]{repo}[/]\n"
                f"[light_green]Size[/]: {size:,} KB\n"
                f"[light_green]Stargazers[/]: {stars:,}\n"
                f"[light_green]Issues/Pull Requests[/]: {issues:,}\n"
                f"[light_green]Forks[/]: {forks:,}",
                expand=False,
                border_style="green",
                title="GitHub",
            )
        )

stats_url = f"https://pypistats.org/api/packages/{package_name}/recent"
with console.status("Getting statistics from PyPI Stats"):
    r = session.get(stats_url)
try:
    parsed_stats = json.loads(r.text)
    assert isinstance(parsed_stats, dict)
except (json.JSONDecodeError, AssertionError):
    parsed_stats = None

stats = parsed_stats["data"] if parsed_stats else None
if stats:
    metadata.add_row(
        Panel(
            f"[blue]Last Month[/]: {stats['last_month']:,}\n"
            f"[blue]Last Week[/]: {stats['last_week']:,}\n"
            f"[blue]Last Day[/]: {stats['last_day']:,}",
            expand=False,
            border_style="yellow",
            title="Downloads",
        )
    )

if info["requires_dist"]:
    metadata.add_row(
        Panel(
            "\n".join(
                f"[light_red link={base_url}/project/{name.split()[0]}]{name}[/]" for name in info["requires_dist"]
            ),
            expand=False,
            border_style="red",
            title="Requirements",
        )
    )
metadata.add_row(
    Panel(
        "\n".join(
            i
            for i in (
                f"[dark_goldenrod]License[/]: {info['license']}",
                f"[dark_goldenrod]Author[/]: {info['author']}",
                f"[dark_goldenrod]Author Email[/]: {info['author_email']}" if info["author_email"] else "",
                f"[dark_goldenrod]Maintainer[/]: {info['maintainer']}" if info["maintainer"] else "",
                f"[dark_goldenrod]Maintainer Email[/]: {info['maintainer_email']}" if info["maintainer_email"] else "",
                f"[dark_goldenrod]Requires Python[/]: {info['requires_python'] or None}",
            )
            if i
        ),
        expand=False,
        border_style="yellow1",
        title="Meta",
    )
)

metadata.add_row(
    Panel(
        _format_classifiers("\n".join(info["classifiers"])).strip(),
        expand=False,
        border_style="cyan",
        title="Classifiers",
    )
)
console.print(Panel(table, border_style="green"))
console.print(metadata)
