import re

import pymupdf
import pymupdf4llm
import scrapy
from markdownify import markdownify
from scrapy.exceptions import NotSupported

from ..document_classifier import DocumentType, get_document_type, should_get_content
from ..services.fnv import fnv1a_64


class CacOutcomeSpider(scrapy.Spider):
    name = "cac-outcomes"

    start_year = 2014
    url_prefix = "https://www.gov.uk/government/collections/cac-outcomes-"

    async def start(self):
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
        last_updated = (
            response.css("meta[name='govuk:public-updated-at']::attr(content)")
            .get()
            .strip()
        )
        outcome_title = response.css("main#content h1::text").get().strip()
        outcome_title = re.sub(
            r"^CAC Outcome:\s*", "", outcome_title, flags=re.RegexFlag.IGNORECASE
        )
        reference = response.css("section#documents p::text").re_first(
            r"^Ref:\s*(TUR\d+/\s?\d+[\/\(]\d+\)?).*"
        )
        if not reference:
            self.logger.warning(
                f"Could not parse reference for '{outcome_title}' at {response.url}"
            )
            reference = response.url
        else:
            reference = reference.replace(" ", "")

        for document in response.css("section#documents > section"):
            decision_link = document.css("h3 a")
            document_title = decision_link.css("*::text").get().strip()
            document_type = get_document_type(document_title)
            common_fields = {
                "year": year,
                "reference": reference,
                "last_updated": last_updated,
                "outcome_url": response.url,
                "outcome_title": outcome_title,
                "document_type": document_type,
            }

            if not should_get_content(document_type):
                document_url = response.urljoin(decision_link.attrib["href"])
                yield {
                    **common_fields,
                    "document_url": document_url,
                    "document_fingerprint": document_url,
                }
            else:
                yield from response.follow_all(
                    urls=decision_link,
                    callback=self.parse_document,
                    cb_kwargs=common_fields,
                )

    def parse_document(self, response, **kwargs):
        document_fingerprint = response.url
        try:
            content = self.html_content(response)
            document_fingerprint = fnv1a_64(content)
            # Bit of a hack, oops :)
            if kwargs["document_type"] == DocumentType.method_agreed:
                published_date = response.css(
                    "meta[name='govuk:first-published-at']::attr(content)"
                ).get()
                content = f"First published at: {published_date}"
        except NotSupported:
            if response.headers.get("Content-Type").decode() == "application/pdf":
                content = self.pdf_content(response)
            else:
                content = ""
        yield {
            **kwargs,
            "document_content": content.strip(),
            "document_url": response.url,
            "document_fingerprint": document_fingerprint,
        }

    def html_content(self, response):
        content = response.css("main#content div#contents div.govspeak").get().strip()
        return markdownify(content)

    def pdf_content(self, response):
        pdf = pymupdf.open(stream=response.body)
        return pymupdf4llm.to_markdown(pdf)
