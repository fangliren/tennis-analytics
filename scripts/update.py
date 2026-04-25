import argparse

from parse.schedule import download_schedule, parse_schedule, SCHEDULE_LOCAL_DIR
from parse.results  import download_results, parse_results, RESULTS_LOCAL_DIR
from parse.combine  import combine, SCHEDULE_TABLES_DIR, RESULTS_TABLES_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and parse the latest tennis league data.")
    parser.add_argument("--refresh-schedule", action="store_true", default=False,
                        help="Re-download and re-parse the schedule (rarely needed).")
    parser.add_argument("--no-results", action="store_true", default=False,
                        help="Skip re-downloading and re-parsing results.")
    parser.add_argument("--no-combine", action="store_true", default=False,
                        help="Skip regenerating the combined table.")
    args = parser.parse_args()

    if args.refresh_schedule:
        download_schedule()
        parse_schedule(sorted(SCHEDULE_LOCAL_DIR.glob("*.xlsx"))[-1])

    if not args.no_results:
        download_results()
        parse_results(sorted(RESULTS_LOCAL_DIR.glob("*.xls"))[-1])

    if not args.no_combine:
        combine(
            SCHEDULE_TABLES_DIR / "schedule.csv",
            RESULTS_TABLES_DIR  / "results.csv",
        )


if __name__ == "__main__":
    main()
