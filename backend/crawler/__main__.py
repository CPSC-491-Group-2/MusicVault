from __future__ import annotations

import argparse
import logging
import os
from datetime import timedelta

from db.queries import catalog, crawl_jobs
from db.session import SessionLocal

from .jobs import KIND_EXPAND_ARTIST, LANE_DEEZER
from .runtime import configure_logging, install_signal_handlers, make_client, run_lane

log = logging.getLogger("crawler.main")


def main() -> None:
    parser = argparse.ArgumentParser(prog="crawler")
    subcommands = parser.add_subparsers(dest="command", required=True)

    seed = subcommands.add_parser(
        "seed", help="queue artists, then crawl the queue dry"
    )
    seed.add_argument("--chart", action="store_true", help="seed the Deezer chart")
    seed.add_argument("--artist", help="seed one Deezer artist id")
    seed.add_argument("--depth", type=int, default=1)
    seed.add_argument("--max-artists", type=int, default=500)
    seed.add_argument("--requeue-age", type=int, default=86400)

    subcommands.add_parser("lanes", help="run the lane workers until signalled")
    subcommands.add_parser("status", help="print queue counts")

    args = parser.parse_args()
    configure_logging()

    if args.command == "seed":
        if not args.chart and not args.artist:
            parser.error("pass --chart, --artist <deezer id>, or both")
        install_signal_handlers()
        run_seed(args)
    elif args.command == "lanes":
        install_signal_handlers()
        run_lane(
            LANE_DEEZER,
            drain=False,
            max_artists=int(os.environ.get("CRAWLER_MAX_ARTISTS", "500")),
        )
    else:
        print_status()


def run_seed(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        targets: list[str] = []
        if args.chart:
            client = make_client()
            chart = client.chart_artists(limit=min(args.max_artists, 100))
            targets.extend(entry["deezer_id"] for entry in chart)
        if args.artist:
            targets.append(args.artist)

        for target in targets:
            crawl_jobs.enqueue(
                db,
                kind=KIND_EXPAND_ARTIST,
                lane=LANE_DEEZER,
                target=target,
                payload={"depth": args.depth},
                priority=crawl_jobs.PRIORITY_SEED,
                requeue_age=timedelta(seconds=args.requeue_age),
            )
        log.info("seeded %s targets at depth=%s", len(targets), args.depth)
    finally:
        db.close()

    run_lane(LANE_DEEZER, drain=True, max_artists=args.max_artists)

    db = SessionLocal()
    try:
        counts = catalog.catalog_counts(db)
        log.info(
            "catalog %s", " ".join(f"{name}={value}" for name, value in counts.items())
        )
        # Drain stops when nothing is due, so a backed-off retry can outlive it.
        unfinished = [
            f"{status}={count}"
            for lane, status, count in crawl_jobs.status_counts(db)
            if lane == LANE_DEEZER and status != "done"
        ]
        if unfinished:
            log.warning("lane not drained dry: %s", " ".join(unfinished))
    finally:
        db.close()


def print_status() -> None:
    db = SessionLocal()
    try:
        counts = crawl_jobs.status_counts(db)
        for lane, status, count in counts:
            print(f"{lane} {status} {count}")
        if not counts:
            print("no jobs")
        age = crawl_jobs.oldest_queued_age(db)
        if age is None:
            print("oldest queued: none")
        else:
            print(f"oldest queued: {int(age.total_seconds())}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
