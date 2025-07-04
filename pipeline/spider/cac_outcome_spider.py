import re
from urllib.parse import urlparse
import os
from abc import ABC, abstractmethod
from itemadapter import ItemAdapter

import pymupdf
import pymupdf4llm
import scrapy
from markdownify import markdownify
from scrapy.exceptions import NotSupported

from ..document_classifier import DocumentType, get_document_type, should_get_content
from ..services.opensearch_pipeline import OpensearchPipeline
from ..services.fnv import fnv1a_64


class CacOutcomeOpensearchPipeline(OpensearchPipeline):
    def fingerprint(self, item):
        data = ItemAdapter(item).asdict()
        document_type = data["document_type"]
        document_url = data["document_url"]
        document_content = data.get("document_content")
        if (
            not should_get_content(document_type)
            or document_url.endswith(".pdf")
            or not document_content
        ):
            return fnv1a_64(document_url)
        return fnv1a_64(document_content)

    async def skip_item(self, item):
        match ItemAdapter(item)["document_type"]:
            case DocumentType.derecognition_decision:
                return "Skipping a derecognition decision"
            case _:
                False

    def id(self, item):
        return item["reference"]

    def doc(self, item):
        data = ItemAdapter(item).asdict()
        document_content = data.pop("document_content", None)
        document_url = data.pop("document_url", None)
        document_type = data.pop("document_type")
        document_fingerprint = self.fingerprint(item)
        return {
            **data,
            "documents": {document_type: document_content},
            "document_urls": {document_type: document_url},
            "document_fingerprints": {document_type: document_fingerprint},
        }


class CacOutcomeSpider(scrapy.Spider, ABC):
    outcome_url_prefix = "https://www.gov.uk/government/publications/cac-outcome"
    list_url_prefix = "https://www.gov.uk/government/collections/cac-outcomes-"

    @abstractmethod
    async def start(self):
        pass

    def parse(self, response, **kwargs):
        if response.url.startswith(self.outcome_url_prefix) and os.path.basename(
            urlparse(response.url).path
        ).startswith("cac-outcome"):
            yield from self.parse_outcome(response, **kwargs)
        else:
            yield from self.parse_document(response, **kwargs)

    def parse_outcome(self, response):
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
                }
            else:
                yield from response.follow_all(
                    urls=decision_link,
                    cb_kwargs=common_fields,
                )

    def parse_document(self, response, **kwargs):
        try:
            content = self.html_content(response)
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
        }

    def html_content(self, response):
        content = response.css("main#content div#contents div.govspeak").get().strip()
        return markdownify(content)

    def pdf_content(self, response):
        pdf = pymupdf.open(stream=response.body)
        return pymupdf4llm.to_markdown(pdf)
