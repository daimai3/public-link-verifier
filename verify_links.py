#!/usr/bin/env python3
"""Check whether public source pages contain an exact link to a target URL."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append((values["href"], values.get("rel") or ""))
        if tag == "meta" and (values.get("name") or "").lower() in {"robots", "googlebot"}:
            self.noindex |= bool(re.search(r"(?:^|[,\s])noindex(?:[,\s]|$)", values.get("content") or "", re.I))


def normalized_url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("올바른 웹 주소가 아닙니다")
    host = parts.hostname.lower()
    port = f":{parts.port}" if parts.port else ""
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urlunsplit((parts.scheme.lower(), host + port, path.rstrip("/") or "/", parts.query, ""))


def inspect(source: str, target: str, timeout: float = 15.0) -> dict[str, str | int | bool]:
    result: dict[str, str | int | bool] = {
        "source_url": source,
        "target_url": target,
        "final_url": "",
        "http_status": 0,
        "exact_href": False,
        "noindex": False,
        "link_rel": "",
        "error": "",
    }
    try:
        request = Request(source, headers={"User-Agent": "PublicLinkVerifier/1.0 (+https://github.com/daimai3/public-link-verifier)"})
        with urlopen(request, timeout=timeout) as response:
            result["http_status"] = response.status
            result["final_url"] = response.url
            result["noindex"] = bool(re.search(r"(?:^|[,\s])noindex(?:[,\s]|$)", response.headers.get("X-Robots-Tag", ""), re.I))
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read(3_000_000).decode(charset, errors="replace")
        parser = PageParser()
        parser.feed(body)
        result["noindex"] = bool(result["noindex"] or parser.noindex)
        wanted = normalized_url(target)
        for href, rel in parser.links:
            try:
                if normalized_url(urljoin(str(result["final_url"]), href)) == wanted:
                    result["exact_href"] = True
                    result["link_rel"] = rel
                    break
            except ValueError:
                continue
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        result["error"] = str(error)[:180]
        if isinstance(error, HTTPError):
            result["http_status"] = error.code
    return result


def main() -> int:
    command = argparse.ArgumentParser(description="공개 페이지의 정확한 링크와 검색 제외 표시를 확인합니다.")
    command.add_argument("--target", required=True, help="확인할 대상 웹 주소")
    command.add_argument("--sources", required=True, help="출처 웹 주소가 한 줄에 하나씩 있는 파일")
    command.add_argument("--output", required=True, help="결과를 저장할 CSV 파일")
    args = command.parse_args()
    try:
        target = normalized_url(args.target)
        with open(args.sources, encoding="utf-8") as source_file:
            sources = [line.strip() for line in source_file if line.strip() and not line.lstrip().startswith("#")]
        rows = [inspect(source, target) for source in dict.fromkeys(sources)]
        with open(args.output, "w", encoding="utf-8", newline="") as result_file:
            writer = csv.DictWriter(result_file, fieldnames=list(rows[0]) if rows else ["source_url", "target_url", "final_url", "http_status", "exact_href", "noindex", "link_rel", "error"])
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, ValueError) as error:
        print(f"확인할 수 없습니다: {error}", file=sys.stderr)
        return 2
    confirmed = sum(bool(row["exact_href"]) and not bool(row["noindex"]) and row["http_status"] == 200 for row in rows)
    print(f"확인한 페이지: {len(rows)}개 · 공개 링크: {confirmed}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
