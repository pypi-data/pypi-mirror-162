from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
from pathlib import Path
import click
import arrow
import toml
from tabulate import tabulate

DOTFILE = Path.home() / ".clock"

def parse_timezone(text):
    """Finds and returns a time zone string matching `text`.
    If multiple time zone strings match, prompts the user to select one.
    If none match, raises an error.
    """
    matches = [tz for tz in available_timezones() if text.lower() in tz.lower()]
    if len(matches) == 0:
        raise ValueError(f"No timezones matched '{text}'.")
    elif len(matches) > 1:
        click.echo("Multiple time zones matched '{text}.' Which is correct?")
        for i, choice in enumerate(matches):
            click.echo(f"{i}. {choice}")
        choice = click.prompt('> ', type=click.IntRange(min=0, max_open=len(matches)), show_choices=False)
        return matches[choice]
    else:
        return matches[0]

def local_timezone():
    return datetime.utcnow().astimezone().tzinfo

def write_dotfile(data):
    with DOTFILE.open('w') as fh:
        toml.dump(data, fh)
    
def read_dotfile():
    if not DOTFILE.exists():
        write_dotfile({"timezones": []})
    with DOTFILE.open('r') as fh:
        return toml.load(fh)

@click.command
@click.argument('time')
@click.option('-t', '--timezone', help="Time zone of input time")
@click.option('-f', '--format', 'fmt', help="Output time format")
@click.option('-d', '--debug', is_flag=True, help="Show debug messages")
@click.option('--add', help="Add a time zone")
def cli(time, timezone, fmt, debug, add):
    "Shows a time in multiple time zones."
    fmt = fmt or 'YYYY-MM-DD HH:mm ZZ'
    tz = parse_timezone(timezone) if timezone else local_timezone()
    ts = arrow.get(time, tzinfo=tz)
    if debug:
        ts_utc = ts.to('UTC')
        click.echo(f"User data saved in {DOTFILE}", color="gray")
        click.echo(f"Using datetime format '{fmt}'", color="gray")
        click.echo(f"Read input '{time}' as {ts} ({ts_utc})", color="gray")
    userdata = read_dotfile()
    if add:
        new_tz = parse_timezone(add)
        if new_tz in userdata['timezones']:
            raise ValueError(f"{new_tz} is already in the list of timezones.")
        userdata['timezones'].append(new_tz)
        write_dotfile(userdata)
    if len(userdata['timezones']) == 0:
        raise ValueError("No time zones are saved. Use --add to add a time zone")
    results = [[tz, ts.to(tz).format(fmt)] for tz in userdata['timezones']]
    click.echo(tabulate(results, ["Time zone", "Local time"]))

if __name__ == '__main__':
    cli()
