import httpx
import pymupdf
import pymupdf4llm
import pytest
from dotenv import find_dotenv, load_dotenv
from markdownify import markdownify
from parsel import Selector


def pytest_configure(config):
    env_file = find_dotenv("dev.env")
    load_dotenv(env_file)


@pytest.fixture()
async def cac_document_contents(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.headers.get("Content-Type") == "application/pdf":
            pdf = pymupdf.open(stream=response.content)
            return pymupdf4llm.to_markdown(pdf)
        else:
            selector = Selector(text=response.text)
            content = (
                selector.css("main#content div#contents div.govspeak").get().strip()
            )
            return markdownify(content)
