# CAC pipeline

## Download the archived Part I site

`scripts/download_part_i_archive.py` downloads the 2014 UK Government Web
Archive snapshot of the CAC Schedule A1 Part I indexes and every HTML, Word, or
PDF resource linked from those indexes. It also downloads the complete page
assets referenced by the HTML and CSS, including stylesheets, scripts, images,
fonts, and icons. Page HTML is stored unchanged, including navigation bars; the
crawler does not follow navigation links into unrelated CAC sections.

From this directory:

```bash
# Download, build the WARC, and verify all checksums.
uv run python scripts/download_part_i_archive.py \
  --output part-i-archive

# Verify an existing archive without making network requests.
uv run python scripts/download_part_i_archive.py \
  --output part-i-archive \
  --verify-only
```

The output directory contains `part-i.warc.gz`, `manifest.jsonl`, and the
response `cache/`. Re-running the command uses the cache and rebuilds and
verifies the WARC. Use `--refresh` to fetch everything again, `--delay N` to
adjust the default 0.05-second request interval, or `--limit N` for a smoke run.
Progress bars report year discovery, downloads, cache hits, errors, WARC
writing, and verification.

### Replay and scrape locally

[pywb](https://pywb.readthedocs.io/) serves WARC records over HTTP and rewrites
links during replay. It is intentionally run as a standalone tool rather than
installed into the pipeline:

```bash
mkdir -p part-i-replay
cd part-i-replay

uvx --from pywb wb-manager init part-i
uvx --from pywb wb-manager add part-i ../part-i-archive/part-i.warc.gz
uvx --from pywb wayback
```

The original root is then available at:

```text
http://localhost:8080/part-i/20140701192925mp_/http://www.cac.gov.uk/index.aspx?articleid=2241
```

Point an ordinary HTTP scraper at that local URL. pywb serves the original
response bodies and the `mp_` replay mode rewrites links to other records in the
local collection. Use `id_` in place of `mp_` when you need the unmodified HTML
without link rewriting. The WARC files themselves are not modified.
