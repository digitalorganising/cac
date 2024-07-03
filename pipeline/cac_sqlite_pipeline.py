import json
import sqlite3
from contextlib import closing

from itemadapter import ItemAdapter


class CacSqlitePipeline:
    commit_frequency = 10

    def __init__(self, db_name):
        self.current_commit = 0
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_name=crawler.settings.get("PIPELINE_DB_NAME"))

    def open_spider(self, spider):
        self.db = sqlite3.connect(self.db_name)

        with closing(self.db.cursor()) as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS outcomes ("
                "    reference TEXT PRIMARY KEY,"
                "    title TEXT,"
                "    documents JSON"
                ")"
            )

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        data["documents"] = json.dumps(
            {data.get("document_type"): data.get("document_content")}
        )
        with closing(self.db.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO outcomes (reference, title, documents)"
                "VALUES (:reference, :outcome_title, json(:documents))"
                "ON CONFLICT (reference)"
                "DO UPDATE SET documents = json_patch(documents, excluded.documents)",
                data,
            )
            self.current_commit += 1
            if self.current_commit == self.commit_frequency:
                self.db.commit()
                self.current_commit = 0
            return item
