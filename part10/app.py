#!/usr/bin/env python3
"""
Part 10 starter.

WHAT'S NEW IN PART 10
You will write two classes without detailed instructions! This is a refactoring, we are not adding new functionality 🙄.
"""

# ToDo 1: You will need to move and change some imports
import time
from constants import BANNER, HELP
from file_utilities import Loader, Printer, Configuration
from models import SearchEngine, ConfigOption

def main() -> None:
    print(BANNER)
    # ToDo 1: Depending on how your imports look, you may need to adapt the call to load_config()
    config = Configuration.load()

    # Load sonnets (from cache or API)
    start = time.perf_counter()
    # ToDo 1: Depending on how your imports look, you may need to adapt the call to load_sonnets()
    sonnets = Loader.load_sonnets()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]")

    print(f"Loaded {len(sonnets)} sonnets.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

        ########insert handle method + 3 instances##############
        handlers = [
            ConfigOption("highlight", ["on", "off"]),
            ConfigOption("search-mode", ["AND", "OR"]),
            ConfigOption("hl-mode", ["DEFAULT", "GREEN"])
        ]
        if raw.startswith(":"):
            handled = False

            for h in handlers:
                if h.handling(raw, config):
                    handled = True
                    break

            if not handled:
                print("Unknown command. Type :help for commands.")

            continue


        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue
        #moved query into new class SearchEngine in models
        start = time.perf_counter()
        engine = SearchEngine(sonnets)
        combined_results = engine.search(raw, config.search_mode)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        elapsed_ms = (time.perf_counter() - start) * 1000

        # ToDo 2: You will need to pass the new setting, the highlight_mode to print_results and use it there

        Printer.print_results(raw, combined_results, highlight=config.highlight, hl_mode= config.hl_mode, query_time_ms=elapsed_ms)


if __name__ == "__main__":
    main()
