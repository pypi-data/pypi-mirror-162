#!/usr/bin/env python3
"""Generate a summary of the parkrun performances of a group of people."""
import argparse
import datetime
import itertools
import json
from pathlib import Path
from string import Template

from . import download
from . import html_construct as html
from .html_construct import a, td, th
from .runner import Runner
from .times import Time

__version__ = "0.0.1"


def abs_path(path):
    return Path(__file__).parent / path


EVENTS = td("Events", class_="text")
COUNT = td("Count", class_="text")
PB = td("PB")


MAIN_SUBROWS = {
    td("Count", class_="text"): lambda r: td(r.runs),
    td("PB"): lambda r: td(r.pb),
}
OVERALL_SUBROWS = {
    EVENTS: lambda r, j: td(len(r.parkrun_data)),
    COUNT: lambda r, j: (
        td(r.total_junior_parkruns, class_=f"b{r.band}" if r.band else None)
    )
    if j
    else td(r.total_parkruns, class_=f"s{r.shirt}" if r.shirt else None),
    PB: lambda r, j: td(r.pb) if r else td(),
}
TOTAL_SUBROWS = {
    td("Count", class_="text"): lambda x: td(sum(i.runs for i in x), class_="total"),
    td("PB"): lambda x: td(min(i.pb for i in x), class_="total"),
}
TOTAL_OVERALL_SUBROWS = {
    EVENTS: lambda x: td(len({i.event for r in x for i in r.parkrun_data})),
    COUNT: lambda x: td(sum(j.runs for r in x for j in r.parkrun_data)),
    PB: lambda x: td(min(i.pb for i in x)),
}


def make_table(runners, junior=False):
    parkruns = set()
    for runner in runners:
        parkruns.update(x.event for x in runner.parkrun_data)
    parkruns = sorted(parkruns)
    maintable = [
        [
            th(h)
            for h in (
                ["parkrun", ""]
                + [a(r.name.split(" ")[0], download.url(r.runner_id)) for r in runners]
                + ["Overall"]
            )
        ]
    ]
    # Make top "Overall" rows
    for subrow in OVERALL_SUBROWS:
        row = [td(), subrow]
        row += [OVERALL_SUBROWS[subrow](runner, junior) for runner in runners]
        row.append(TOTAL_OVERALL_SUBROWS[subrow](runners))
        maintable.append(
            f'<tr class="total{"" if subrow == PB else " count"}">{"".join(row)}</tr>'
        )

    # Make main table
    for parkrun in parkruns:
        for i, subrow in enumerate(MAIN_SUBROWS):
            initial = td(parkrun, class_="text") if i == 0 else td()
            row = [initial, subrow]
            for r in runners:
                data = r.get_parkrun_data(parkrun)
                row.append(td() if data is None else MAIN_SUBROWS[subrow](data))
            row.append(
                TOTAL_SUBROWS[subrow](
                    r.get_parkrun_data(parkrun)
                    for r in runners
                    if r.get_parkrun_data(parkrun) is not None
                )
            )
            maintable.append(
                f'<tr class="count">{"".join(row)}</tr>'
                if subrow == td("Count", class_="text")
                else row
            )

    return html.create_html_table(maintable, "main")


def make_recents_table(runners):
    runs = sorted(
        itertools.chain.from_iterable(
            [(run, runner.name) for run in runner.recents] for runner in runners
        ),
        key=lambda r: (-r[0].run_date.toordinal(), r[0].event, r[0].overall_pos),
    )
    table = [
        [
            th(x)
            for x in (
                "Date",
                "Event",
                "Runner",
                "Gender Pos",
                "Overall Pos",
                "Time",
                "Age Grade",
            )
        ]
    ]
    previous_run = None
    had_dates = set()
    colour = 1
    for run, runner_name in runs:
        if (run.run_date, run.event) != previous_run:
            colour = 1 - colour
            previous_run = (run.run_date, run.event)

        overline = False
        if run.run_date not in had_dates:
            if had_dates:
                overline = True
            had_dates.add(run.run_date)
            if len(had_dates) > 3:
                break
        row = "".join(
            (
                td(run.run_date, align="c"),
                td(run.event),
                td(runner_name.split(" ")[0]),
                td(format(run.gender_pos, "\N{FIGURE SPACE}>3"), align="c"),
                td(format(run.overall_pos, "\N{FIGURE SPACE}>3"), align="c"),
                td(Time(run.time), align="c"),
                td(run.age_grade, align="c"),
            )
        )
        classes = []
        if colour:
            classes.append("shaded")
        if overline:
            classes.append("overline")
        class_ = f' class="{" ".join(classes)}"' if classes else ""
        table.append(f"<tr{class_}>{row}</tr>")
    return html.create_html_table(table)


def main():
    parser = argparse.ArgumentParser(
        description="Create a family parkrun summary from a list of runners"
    )
    parser.add_argument(
        "--download",
        "-d",
        metavar="runner_list",
        type=argparse.FileType("r"),
        help="download data from the website",
    )
    args = parser.parse_args()
    if args.download:
        with args.download as f:
            runners = f.read().strip("\n").splitlines()
        runners = [download.get_runner_stats(r) for r in runners]
        with open("saved_data.json", "w") as f:
            json.dump(
                runners,
                f,
                default=lambda x: Runner.serialise(x)
                if isinstance(x, Runner)
                else x.isoformat(),
                separators=(",", ":"),
            )
    else:
        with open("saved_data.json") as f:
            runners = json.load(f)
        runners = [
            Runner(
                name=r["name"],
                runner_id=r["runner_id"],
                parkrun_data=[
                    download.PersonParkrunStats(
                        p[0], p[1], p[2], p[3], Time(p[4]), p[5]
                    )
                    for p in r["parkrun_data"]
                ],
                recents=[
                    download.RecentRun(
                        p[0],
                        datetime.date.fromisoformat(p[1]),
                        p[2],
                        p[3],
                        Time(p[4]),
                        p[5],
                    )
                    for p in r["recents"]
                ],
                junior=r["junior"],
            )
            for r in runners
        ]

    senior_runners = []
    junior_runners = []
    for runner in runners:
        senior_data = [r for r in runner.parkrun_data if not r.junior]
        junior_data = [r for r in runner.parkrun_data if r.junior]
        if senior_data:
            senior_runners.append(
                Runner(
                    runner.name, runner.runner_id, senior_data, [], bool(junior_data)
                )
            )
        if junior_data:
            junior_runners.append(
                Runner(runner.name, runner.runner_id, junior_data, [], True)
            )
    Path("summary.html").write_text(
        Template(abs_path("page.html").read_text()).substitute(
            {
                "css": abs_path("style.css").read_text(),
                "senior": make_table(senior_runners),
                "junior": make_table(junior_runners, True),
                "recents": make_recents_table(runners),
            }
        )
    )


if __name__ == "__main__":
    main()
