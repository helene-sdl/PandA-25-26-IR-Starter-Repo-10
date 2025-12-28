from __future__ import annotations
from typing import List, Dict, Any, Tuple



class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)

class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: list[LineMatch], matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)

    # ToDo 0: Moved to SearchResult
    @staticmethod
    def ansi_highlight(text: str, spans, mode: str = "DEFAULT"):
        """Return text with ANSI highlight escape codes inserted."""
        if not spans:
            return text

        spans = sorted(spans)
        merged = []

        # Merge overlapping spans
        current_start, current_end = spans[0]
        for s, e in spans[1:]:
            if s <= current_end:
                current_end = max(current_end, e)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = s, e
        merged.append((current_start, current_end))

        # Build highlighted string
        if mode == "GREEN":
            start_code = "\033[1;92m" #light green, run start code below depending on this conditional statement
        else:
            start_code = "\033[43m\033[30m" #yellow, black background
        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            # ToDo 2: You will need to use the new setting and for it a different ANSI color code: "\033[1;92m"
            out.append(start_code)
            out.append(text[s:e])
            # ToDo 2: This stays the same. It just means "continue with default colors"
            out.append("\033[0m")  # reset
            i = e
        out.append(text[i:])
        return "".join(out)

    # ToDo 0: Moved to SearchResult
    def combine_results(self, other: "SearchResult") -> "SearchResult":
        """Combine two search results."""

        combined = self.copy()  # shallow cop

        combined.matches = self.matches + other.matches
        combined.title_spans = sorted(self.title_spans + other.title_spans)

        # Merge line_matches by line number

        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in other.line_matches:
            ln = lm.line_no
            if ln in lines_by_no:
                # extend spans & keep original text
                lines_by_no[ln].spans.extend(lm.spans)
            else:
                lines_by_no[ln] = lm.copy()

        combined.line_matches = sorted(lines_by_no.values(), key=lambda lm: lm.line_no)

        return combined



class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

    # ToDo 0: Moved to Sonnet
    @staticmethod
    def find_spans(text: str, pattern: str):
        """Return [(start, end), ...] for all (possibly overlapping) matches.
        Inputs should already be lowercased by the caller."""
        spans = []
        if not pattern:
            return spans

        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                spans.append((i, i + len(pattern)))
        return spans

    # ToDo 0: Moved to sonnet and renamed
    def search_for(self, query: str) -> SearchResult:
        title_raw = str(self.title)
        lines_raw = self.lines

        q = query.lower()
        title_spans = Sonnet.find_spans(title_raw.lower(), q)

        line_matches = []
        for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
            spans = Sonnet.find_spans(line_raw.lower(), q)
            if spans:
                line_matches.append(LineMatch(idx, line_raw, spans))

        total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)

        return SearchResult(title_raw, title_spans, line_matches, total)

class SearchEngine:
    def __init__(self, sonnets):
        self.sonnets = sonnets

    def search(self, query: str, search_mode:str ):
    # query
        combined_results = []
        words = query.split()

        for word in words:
            # Searching for the word in all sonnets
            # ToDo 0:You will need to adapt the call to search_sonnet
            results = [s.search_for(word) for s in self.sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    if search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            # ToDo 0:You will need to adapt the call to combine_results
                            combined_results[i] = combined_result.combine_results(result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif search_mode == "OR":
                        # ToDo 0:You will need to adapt the call to combine_results
                        combined_results[i] = combined_result.combine_results(result)
        return combined_results

class ConfigOption:
    def __init__(self, command, valid_values):
        self.command = command
        self.valid_values = valid_values

    def handling(self, raw, config):
        if not raw.startswith(f":{self.command}"):
            return False

        parts = raw.split()
        if len(parts) != 2:
            print("Usage:  :", self.command, "|".join(self.valid_values))
            return True

        value = parts[1]

        if value.upper() not in [v.upper() for v in self.valid_values]:
            print("Usage:  :", self.command, "|".join(self.valid_values))
            return True

        if self.command == "highlight":
            config.highlight = (value.lower() == "on")
            print("Highlighting", "ON" if config.highlight else "OFF")

        elif self.command == "search-mode":
            config.search_mode = value.upper()
            print("Search mode set to", config.search_mode)

        elif self.command == "hl-mode":
            config.hl_mode = value.upper()
            print("Highlighting mode set to", config.hl_mode)

        config.save()
        return True




