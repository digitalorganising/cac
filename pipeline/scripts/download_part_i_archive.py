#!/usr/bin/env -S uv run python
"""Download the archived CAC Part I indexes and their linked resources to WARC."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from scrapy import Selector
from tqdm import tqdm
from warcio.archiveiterator import ArchiveIterator
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter

DEFAULT_START_URL = (
    "https://webarchive.nationalarchives.gov.uk/ukgwa/20140701192925/"
    "http://www.cac.gov.uk/index.aspx?articleid=2241"
)
ARCHIVE_URL_RE = re.compile(
    r"^https?://webarchive\.nationalarchives\.gov\.uk/ukgwa/"
    r"(?P<timestamp>\d{14})(?P<modifier>[a-z]{2}_)?/"
    r"(?P<original>https?://.+)$",
    re.IGNORECASE,
)
CAPTURE_URL_RE = re.compile(r"/ukgwa/(?P<timestamp>\d{14})[a-z]{2}_/")
CSS_URL_RE = re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)
CONTENT_START_RE = re.compile(
    rb"<div\s+id=[\"']bodytextcontainer[\"'][^>]*>", re.IGNORECASE
)
CONTENT_END_RE = re.compile(
    rb"<div\s+id=[\"']lowerprintblock[\"'][^>]*>", re.IGNORECASE
)
USER_AGENT = "cac-part-i-archiver/1.0 (one-off research preservation utility)"
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


@dataclass(frozen=True)
class Resource:
    url: str
    kind: str
    source_url: str | None


@dataclass
class CachedResponse:
    original_url: str
    kind: str
    source_url: str | None
    archive_url: str
    capture_timestamp: str
    status: int
    reason: str
    http_version: str
    headers: list[tuple[str, str]]
    sha256: str
    size: int
    cache_key: str


class ResponseCache:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, resource: Resource) -> CachedResponse | None:
        key = self.key(resource.url)
        metadata_path = self.directory / f"{key}.json"
        body_path = self.directory / f"{key}.body"
        if not metadata_path.exists() or not body_path.exists():
            return None
        metadata = json.loads(metadata_path.read_text())
        body = body_path.read_bytes()
        if hashlib.sha256(body).hexdigest() != metadata["sha256"]:
            return None
        metadata["kind"] = resource.kind
        metadata["source_url"] = resource.source_url
        return CachedResponse(**metadata)

    def put(
        self, resource: Resource, response: httpx.Response, timestamp: str
    ) -> CachedResponse:
        key = self.key(resource.url)
        capture_match = CAPTURE_URL_RE.search(str(response.url))
        cached = CachedResponse(
            original_url=resource.url,
            kind=resource.kind,
            source_url=resource.source_url,
            archive_url=str(response.url),
            capture_timestamp=(
                capture_match.group("timestamp") if capture_match else timestamp
            ),
            status=response.status_code,
            reason=response.reason_phrase,
            http_version=response.http_version,
            headers=list(response.headers.multi_items()),
            sha256=hashlib.sha256(response.content).hexdigest(),
            size=len(response.content),
            cache_key=key,
        )
        (self.directory / f"{key}.body").write_bytes(response.content)
        (self.directory / f"{key}.json").write_text(
            json.dumps(asdict(cached), indent=2) + "\n"
        )
        return cached

    def body(self, response: CachedResponse) -> bytes:
        return (self.directory / f"{response.cache_key}.body").read_bytes()


def unwrap_archive_url(url: str) -> tuple[str, str]:
    """Return the requested timestamp and original URL from a UKGWA URL."""
    match = ARCHIVE_URL_RE.match(url)
    if not match:
        raise ValueError(f"Not a supported UKGWA replay URL: {url}")
    return match.group("timestamp"), match.group("original")


def raw_archive_url(timestamp: str, original_url: str) -> str:
    return (
        "https://webarchive.nationalarchives.gov.uk/ukgwa/"
        f"{timestamp}id_/{original_url}"
    )


def normalize_original_url(
    url: str, *, base_url: str | None = None, cac_only: bool = False
) -> str | None:
    if base_url is not None:
        url = urljoin(base_url, url)
    url, _ = urldefrag(url)
    if not url or url.startswith(("javascript:", "mailto:", "tel:")):
        return None

    archive_match = ARCHIVE_URL_RE.match(url)
    if archive_match:
        url = archive_match.group("original")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if cac_only and (parsed.hostname or "").lower() not in {
        "cac.gov.uk",
        "www.cac.gov.uk",
    }:
        return None
    return url


def content_links(body: bytes, base_url: str) -> list[str]:
    start = CONTENT_START_RE.search(body)
    end = CONTENT_END_RE.search(body, start.end() if start else 0)
    if start is None or end is None:
        return []
    # Some older index pages contain malformed table markup that causes an HTML
    # parser to close bodytextcontainer early. Slice on the site's stable print
    # block markers before parsing so those links remain in scope.
    fragment = body[start.end() : end.start()]
    selector = Selector(
        text=f"<div>{fragment.decode('utf-8', errors='replace')}</div>",
        type="html",
    )
    links: list[str] = []
    seen: set[str] = set()
    for href in selector.css("a::attr(href)").getall():
        url = normalize_original_url(href.strip(), base_url=base_url, cac_only=True)
        if url is not None and url not in seen:
            seen.add(url)
            links.append(url)
    return links


def asset_links(body: bytes, base_url: str) -> list[str]:
    """Find page assets without following ordinary navigation links."""
    text = body.decode("utf-8", errors="replace")
    selector = Selector(text=text, type="html")
    candidates = selector.css(
        "script::attr(src), img::attr(src), link::attr(href), "
        "input::attr(src), object::attr(data), embed::attr(src), "
        "source::attr(src)"
    ).getall()
    for srcset in selector.css("source::attr(srcset), img::attr(srcset)").getall():
        candidates.extend(item.strip().split()[0] for item in srcset.split(","))
    candidates.extend(CSS_URL_RE.findall(text))
    return normalized_urls(candidates, base_url)


def css_links(body: bytes, base_url: str) -> list[str]:
    text = body.decode("utf-8", errors="replace")
    candidates = CSS_URL_RE.findall(text)
    candidates.extend(
        re.findall(r"@import\s+[\"']([^\"']+)", text, flags=re.IGNORECASE)
    )
    return normalized_urls(candidates, base_url)


def normalized_urls(candidates: list[str], base_url: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        url = normalize_original_url(candidate.strip(), base_url=base_url)
        if url is not None and url not in seen:
            seen.add(url)
            links.append(url)
    return links


def fetch(
    client: httpx.Client, timestamp: str, original_url: str, delay: float
) -> httpx.Response:
    time.sleep(delay)
    return client.get(raw_archive_url(timestamp, original_url))


def get_resource(
    client: httpx.Client,
    cache: ResponseCache,
    resource: Resource,
    *,
    timestamp: str,
    delay: float,
    refresh: bool,
) -> tuple[CachedResponse, bool]:
    if not refresh and (cached := cache.get(resource)) is not None:
        return cached, True
    response = fetch(client, timestamp, resource.url, delay)
    return cache.put(resource, response, timestamp), False


def content_type(response: CachedResponse) -> str:
    return dict(response.headers).get("content-type", "").lower()


def crawl(
    client: httpx.Client,
    cache: ResponseCache,
    *,
    timestamp: str,
    start_original_url: str,
    delay: float,
    refresh: bool,
    limit: int | None,
) -> tuple[list[CachedResponse], int, int, int]:
    records: dict[str, CachedResponse] = {}
    cache_hits = 0
    downloaded_bytes = 0
    http_errors = 0

    root = Resource(start_original_url, "page", None)
    root_response, hit = get_resource(
        client,
        cache,
        root,
        timestamp=timestamp,
        delay=delay,
        refresh=refresh,
    )
    records[root.url] = root_response
    cache_hits += int(hit)
    downloaded_bytes += 0 if hit else root_response.size

    root_body = cache.body(root_response)
    year_urls = content_links(root_body, start_original_url)
    if not year_urls:
        raise RuntimeError("The Part I root page contained no year links")

    queue: list[Resource] = []
    queued = {root.url, *year_urls}

    def enqueue(url: str, kind: str, source_url: str) -> None:
        if url not in queued:
            queued.add(url)
            queue.append(Resource(url, kind, source_url))

    for url in asset_links(root_body, root.url):
        enqueue(url, "asset", root.url)

    with tqdm(year_urls, desc="Year indexes", unit="page") as progress:
        for year_url in progress:
            resource = Resource(year_url, "page", root.url)
            response, hit = get_resource(
                client,
                cache,
                resource,
                timestamp=timestamp,
                delay=delay,
                refresh=refresh,
            )
            records[year_url] = response
            cache_hits += int(hit)
            downloaded_bytes += 0 if hit else response.size
            body = cache.body(response)
            for url in content_links(body, year_url):
                enqueue(url, "document", year_url)
            for url in asset_links(body, year_url):
                enqueue(url, "asset", year_url)

    processed = 0
    progress_total = min(len(queue), limit) if limit is not None else len(queue)
    with tqdm(
        total=progress_total, desc="Documents and assets", unit="file"
    ) as progress:
        while processed < len(queue) and (limit is None or processed < limit):
            resource = queue[processed]
            processed += 1
            try:
                response, hit = get_resource(
                    client,
                    cache,
                    resource,
                    timestamp=timestamp,
                    delay=delay,
                    refresh=refresh,
                )
                records[resource.url] = response
                cache_hits += int(hit)
                downloaded_bytes += 0 if hit else response.size
                http_errors += int(response.status >= 400)

                body = cache.body(response)
                found: list[str] = []
                if "text/html" in content_type(response):
                    found = asset_links(body, resource.url)
                elif "text/css" in content_type(response):
                    found = css_links(body, resource.url)
                for url in found:
                    before = len(queue)
                    enqueue(url, "asset", resource.url)
                    if limit is None:
                        progress.total += len(queue) - before
            except (httpx.HTTPError, OSError, RuntimeError) as error:
                tqdm.write(f"Failed {resource.url}: {error}", file=sys.stderr)
                http_errors += 1
            progress.update()
            progress.set_postfix(cache_hits=cache_hits, errors=http_errors)

    return list(records.values()), cache_hits, downloaded_bytes, http_errors


def write_response(
    writer: WARCWriter,
    cache: ResponseCache,
    response: CachedResponse,
) -> None:
    headers = [
        (name, value)
        for name, value in response.headers
        if name.lower() not in HOP_BY_HOP_HEADERS and name.lower() != "content-length"
    ]
    body = cache.body(response)
    headers.append(("Content-Length", str(len(body))))
    protocol = response.http_version
    if not protocol.upper().startswith("HTTP/"):
        protocol = f"HTTP/{protocol}"
    http_headers = StatusAndHeaders(
        f"{response.status} {response.reason}",
        headers,
        protocol=protocol,
    )

    capture_date = (
        datetime.strptime(response.capture_timestamp, "%Y%m%d%H%M%S")
        .replace(tzinfo=UTC)
        .isoformat()
        .replace("+00:00", "Z")
    )
    writer.write_record(
        writer.create_warc_record(
            response.original_url,
            "response",
            payload=BytesIO(body),
            http_headers=http_headers,
            warc_headers_dict={
                "WARC-Date": capture_date,
                "WARC-Source-URI": response.archive_url,
            },
        )
    )


def write_outputs(
    output_dir: Path, cache: ResponseCache, records: list[CachedResponse]
) -> None:
    manifest_path = output_dir / "manifest.jsonl"
    with manifest_path.open("w") as manifest:
        for response in records:
            manifest.write(json.dumps(asdict(response), sort_keys=True) + "\n")

    warc_path = output_dir / "part-i.warc.gz"
    with warc_path.open("wb") as stream:
        writer = WARCWriter(stream, gzip=True)
        writer.write_record(
            writer.create_warcinfo_record(
                warc_path.name,
                {
                    "software": USER_AGENT,
                    "format": "WARC File Format 1.1",
                    "description": "UKGWA capture of CAC Schedule A1 Part I",
                },
            )
        )
        for response in tqdm(records, desc="Writing WARC", unit="record"):
            write_response(writer, cache, response)


def verify(output_dir: Path) -> int:
    manifest_path = output_dir / "manifest.jsonl"
    warc_path = output_dir / "part-i.warc.gz"
    records = [
        CachedResponse(**json.loads(line))
        for line in manifest_path.read_text().splitlines()
        if line
    ]

    errors = 0
    expected = {response.original_url: response.sha256 for response in records}
    cache_dir = output_dir / "cache"
    for response in tqdm(records, desc="Verifying cache", unit="file"):
        body_path = cache_dir / f"{response.cache_key}.body"
        if not body_path.exists():
            tqdm.write(f"Missing cached body: {response.original_url}", file=sys.stderr)
            errors += 1
        elif hashlib.sha256(body_path.read_bytes()).hexdigest() != response.sha256:
            tqdm.write(
                f"Cache checksum mismatch: {response.original_url}",
                file=sys.stderr,
            )
            errors += 1

    found: set[str] = set()
    with (
        warc_path.open("rb") as stream,
        tqdm(total=len(records), desc="Verifying WARC", unit="record") as progress,
    ):
        for record in ArchiveIterator(stream):
            if record.rec_type != "response":
                continue
            url = record.rec_headers.get_header("WARC-Target-URI")
            digest = hashlib.sha256(record.content_stream().read()).hexdigest()
            found.add(url)
            if expected.get(url) != digest:
                tqdm.write(f"WARC checksum mismatch: {url}", file=sys.stderr)
                errors += 1
            progress.update()

    for url in expected.keys() - found:
        tqdm.write(f"Missing WARC record: {url}", file=sys.stderr)
        errors += 1
    print(
        f"Verified {len(records):,} cached responses and WARC records"
        + (f" with {errors} error(s)" if errors else "")
    )
    return errors


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def download(args: argparse.Namespace) -> int:
    timestamp, start_original_url = unwrap_archive_url(args.start_url)
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.verify_only:
        return int(verify(output_dir) > 0)

    cache = ResponseCache(output_dir / "cache")
    client = httpx.Client(
        follow_redirects=True,
        timeout=args.timeout,
        transport=httpx.HTTPTransport(retries=args.retries),
        headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
    )
    try:
        records, cache_hits, downloaded_bytes, http_errors = crawl(
            client,
            cache,
            timestamp=timestamp,
            start_original_url=start_original_url,
            delay=args.delay,
            refresh=args.refresh,
            limit=args.limit,
        )
        write_outputs(output_dir, cache, records)
        verification_errors = verify(output_dir)
        print(
            f"Archived {len(records):,} resources to {output_dir / 'part-i.warc.gz'}\n"
            f"Downloaded {human_size(downloaded_bytes)}; "
            f"{cache_hits:,} cache hit(s); {http_errors:,} HTTP/fetch error(s)"
        )
        return int(bool(http_errors or verification_errors))
    finally:
        client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive CAC Schedule A1 Part I from UKGWA to WARC."
    )
    parser.add_argument(
        "--start-url", default=DEFAULT_START_URL, help="UKGWA Part I root URL"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("part-i-archive"),
        help="Archive/cache directory (default: part-i-archive)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        help="Minimum seconds between network requests (default: 0.05)",
    )
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--limit",
        type=int,
        help="Capture at most this many documents/assets after the year indexes",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore cached responses and fetch everything again",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the existing cache, manifest, and WARC without downloading",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sys.exit(download(args))


if __name__ == "__main__":
    main()
