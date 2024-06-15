import pymupdf
import pymupdf4llm
import scrapy
from markdownify import markdownify
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import NotSupported


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
        decision_title = (
            response.css("main#content h1::text")
            .get()
            .strip()
            .removeprefix("CAC Outcome: ")
        )
        reference = response.css("section#documents p::text").re_first(
            r"^Ref:\s*(TUR1/\d+\(\d+\)).*"
        )
        for document in response.css("section#documents > section"):
            outcome_link = document.css("h3 a")
            outcome_title = outcome_link.css("*::text").get().strip()
            yield from response.follow_all(
                urls=outcome_link,
                callback=self.parse_document,
                cb_kwargs={
                    "reference": reference,
                    "decision_title": decision_title,
                    "outcome_title": outcome_title,
                    "year": year,
                },
            )

    def parse_document(self, response, **kwargs):
        try:
            content = self.html_content(response)
        except NotSupported:
            if response.headers.get("Content-Type").decode() == "application/pdf":
                content = self.pdf_content(response)
            else:
                content = ""
        yield {**kwargs, "content": content.strip()}

    def html_content(self, response):
        content = response.css("main#content div#contents div.govspeak").get().strip()
        return markdownify(content)

    def pdf_content(self, response):
        pdf = pymupdf.open(stream=response.body)
        return pymupdf4llm.to_markdown(pdf)


if __name__ == "__main__":
    process = CrawlerProcess(
        settings={
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "LOG_LEVEL": "INFO",
            "FEEDS": {"data/outcomes.json": {"format": "jsonlines"}},
        }
    )
    process.crawl(CacOutcomeSpider)
    process.start()
