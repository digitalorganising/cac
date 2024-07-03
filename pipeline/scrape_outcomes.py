import re

import pymupdf
import pymupdf4llm
import scrapy
from markdownify import markdownify
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import NotSupported

from .cac_sqlite_pipeline import CacSqlitePipeline
from .document_classifier import get_document_type


class CacOutcomeSpider(scrapy.Spider):
    name = "cac-outcomes"

    start_year = 2014
    url_prefix = "https://www.gov.uk/government/collections/cac-outcomes-"

    def start_requests(self):
        yield scrapy.Request(
            url=(self.url_prefix + str(self.start_year)),
            callback=self.parse,
            meta={"year": self.start_year},
        )

    def parse(self, response):
        outcome_links = response.css(
            "h3#trade-union-recognition + " "div + div > ul > li div a"
        )
        yield from response.follow_all(
            urls=outcome_links,
            callback=self.parse_outcome,
            cb_kwargs={"year": response.meta["year"]},
        )

        maybe_next_year = response.meta["year"] + 1
        yield response.follow(
            url=(self.url_prefix + str(maybe_next_year)),
            callback=self.parse,
            meta={"year": maybe_next_year},
        )

    def parse_outcome(self, response, year):
        outcome_title = response.css("main#content h1::text").get().strip()
        outcome_title = re.sub(
            r"^CAC Outcome:\s+", "", outcome_title, flags=re.RegexFlag.IGNORECASE
        )
        reference = response.css("section#documents p::text").re_first(
            r"^Ref:\s*(TUR\d+/\d+[\/\(]\d+\)?).*"
        )
        if not reference:
            self.logger.warning(
                f"Could not parse reference for '{outcome_title}' at {response.url}"
            )
            return

        for document in response.css("section#documents > section"):
            outcome_link = document.css("h3 a")
            document_title = outcome_link.css("*::text").get().strip()
            document_type = get_document_type(document_title)
            common_fields = {
                "year": year,
                "reference": reference,
                "outcome_url": response.url,
                "outcome_title": outcome_title,
                "document_type": document_type,
            }

            if not document_type:
                yield common_fields

            yield from response.follow_all(
                urls=outcome_link, callback=self.parse_document, cb_kwargs=common_fields
            )

    def parse_document(self, response, **kwargs):
        try:
            content = self.html_content(response)
        except NotSupported:
            if response.headers.get("Content-Type").decode() == "application/pdf":
                content = self.pdf_content(response)
            else:
                content = ""
        yield {**kwargs, "document_content": content.strip()}

    def html_content(self, response):
        content = response.css("main#content div#contents div.govspeak").get().strip()
        return markdownify(content)

    def pdf_content(self, response):
        pdf = pymupdf.open(stream=response.body)
        return pymupdf4llm.to_markdown(pdf)


def scrape():
    process = CrawlerProcess(
        settings={
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "LOG_LEVEL": "INFO",
            "FEEDS": {"data/outcomes.json": {"format": "jsonlines"}},
            "PIPELINE_DB_NAME": "data/outcomes.db",
            "ITEM_PIPELINES": {CacSqlitePipeline: 100},
        }
    )
    process.crawl(CacOutcomeSpider)
    process.start()
