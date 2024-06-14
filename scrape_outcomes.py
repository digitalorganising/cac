import scrapy
from scrapy.crawler import CrawlerProcess
from markdownify import markdownify


def get_title(response):
    return response.css("main#content h1::text").get().strip()


class CacOutcomeSpider(scrapy.Spider):
    name = "cac-outcomes"

    start_year = 2020
    url_prefix = "https://www.gov.uk/government/collections/cac-outcomes-"

    def start_requests(self):
        yield scrapy.Request(
            url=(self.url_prefix + str(self.start_year)),
            callback=self.parse,
            meta={
                "year": self.start_year
            }
        )

    def parse(self, response):
        outcome_links = response.css("h3#trade-union-recognition + div + div > ul > li div a")
        yield from response.follow_all(
            urls=outcome_links,
            callback=self.parse_outcome,
            cb_kwargs={"year": response.meta["year"]}
        )

        maybe_next_year = response.meta["year"] + 1
        yield response.follow(
            url=(self.url_prefix + str(maybe_next_year)),
            callback=self.parse,
            meta={
                "year": maybe_next_year
            }
        )

    def parse_outcome(self, response, year):
        decision_title = get_title(response).removeprefix("CAC Outcome: ")
        reference = response.css("section#documents p::text").re_first(r"Ref:\s*(.+)")
        for document in response.css("section#documents > section"):
            yield from response.follow_all(
                urls=document.css("a"),
                callback=self.parse_document,
                cb_kwargs={
                    "reference": reference,
                    "decision_title": decision_title,
                    "year": year
                }
            )

    def parse_document(self, response, reference, decision_title, year):
        try:
            title = get_title(response)
            content = response.css("main#content div#contents div.govspeak").get()
            content_md = markdownify(content).strip()
            yield {
                "reference": reference,
                "decision_title": decision_title,
                "document_title": title,
                "year": str(year)
                # "content": content_md
            }
        except Exception as e:
            raise e


if __name__ == "__main__":
    process = CrawlerProcess(
        settings={
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "FEEDS": {
                "data/outcomes.json": {
                    "format": "jsonlines"
                }
            }
        }
    )
    process.crawl(CacOutcomeSpider)
    process.start()
