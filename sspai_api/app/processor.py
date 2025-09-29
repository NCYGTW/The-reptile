from bs4 import BeautifulSoup
import logging
from app.crawler import SSPAICrawler
from app.database import DatabaseHandler

class DataProcessor:
    """数据处理类"""

    def __init__(self, crawler, db):
        self.crawler = crawler
        self.db = db

    def process_articles(self, pages=10):
        """处理文章数据"""
        for article in self.crawler.get_articles(pages=pages):
            try:
                article_id = article["id"]
                title = article.get("title", "")
                likes = article.get("like_count", 0)
                author = article.get("author", {}).get("nickname", "")
                time = article.get("released_time", 0)

                raw_content = self.crawler.get_article_detail(article_id)
                cleaned_content = BeautifulSoup(raw_content, "lxml").get_text()

                self.db.insert_article((
                    article_id,
                    title,
                    cleaned_content,
                    likes,
                    author,
                    time
                ))

                self._process_comments(article_id)

            except KeyError as e:
                logging.error(f"Missing key in article data: {e}")
            except Exception as e:
                logging.error(f"Process article {article_id} error: {e}")

    def _process_comments(self, article_id):
        """处理评论数据"""
        comments = self.crawler.get_comments(article_id)
        if comments["total"] == 0:
            return

        best_comment = None
        max_replies = -1
        latest_time = 0

        for comment in comments.get("data", []):
            replies = len(comment.get("reply", []))
            created_at = comment.get("created_at", 0)

            if replies > max_replies or (replies == max_replies and created_at > latest_time):
                max_replies = replies
                latest_time = created_at
                best_comment = (
                    comment.get("id"),
                    article_id,
                    comment.get("comment", ""),
                    comment.get("user", {}).get("nickname", ""),
                    created_at
                )

        if best_comment:
            self.db.insert_comment(best_comment)