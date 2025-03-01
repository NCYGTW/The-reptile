import requests
import pymysql
import logging
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "passwd": "Tian1901",
    "database": "app",
    "charset": "utf8mb4"
}

CREATE_ARTICLE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS article_table(
    id INT AUTO_INCREMENT PRIMARY KEY,      #自增主键
    article_id INT NOT NULL,
    article_title TEXT,
    article_text LONGTEXT,
    article_likes INT NOT NULL,
    article_time TIMESTAMP,
    article_author TEXT,
    UNIQUE (article_id)
);
"""

CREATE_BESTCOMMENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bestcomment_table(
    id INT AUTO_INCREMENT PRIMARY KEY,       
    comment_id INT NOT NULL,
    article_id INT NOT NULL,
    best_comment TEXT,
    comment_author TEXT,
    comment_time TIMESTAMP,
    UNIQUE (article_id)
);
"""

ARTICLE_API = {
    "index": "https://sspai.com/api/v1/article/index/page/get",
    "detail": "https://sspai.com/api/v1/article/info/get"
}
COMMENT_API = "https://sspai.com/api/v1/comment/user/article/hot/page/get"


class DatabaseHandler:
    """数据库操作类"""
    def __init__(self):         #类的构造函数，当创建这个类的实例（self）时，就会调用这个函数
        self.connection = pymysql.connect(**config)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建数据表"""
        try:
            self.cursor.execute(CREATE_ARTICLE_TABLE_SQL)
            self.cursor.execute(CREATE_BESTCOMMENT_TABLE_SQL)
            self.connection.commit()
            logging.info("Tables created successfully")
        except Exception as e:
            logging.error(f"Create tables failed: {e}")
            self.connection.rollback()

    def insert_article(self, data):
        """插入文章数据"""
        sql = """
        INSERT IGNORE INTO article_table 
        (article_id, article_title, article_text, article_likes, article_author, article_time)
        VALUES (%s, %s, %s, %s, %s, FROM_UNIXTIME(%s))
        """
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            logging.info(f"Article {data[0]} inserted")
        except pymysql.IntegrityError:
            logging.warning(f"Duplicate article {data[0]} skipped")
        except Exception as e:
            logging.error(f"Insert article error: {e}")
            self.connection.rollback()

    def insert_comment(self, data):
        """插入评论数据"""
        sql = """
        INSERT IGNORE INTO bestcomment_table 
        (comment_id, article_id, best_comment, comment_author, comment_time)
        VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s))
        """
        try:
            self.cursor.execute(sql, data)
            self.connection.commit()
            logging.info(f"Comment for article {data[1]} inserted")
        except pymysql.IntegrityError:
            logging.warning(f"Duplicate comment for article {data[1]} skipped")
        except Exception as e:
            logging.error(f"Insert comment error: {e}")
            self.connection.rollback()

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.connection.close()
        logging.info("Database connection closed")


class SSPAICrawler:
    """请求与获取类"""

    def __init__(self):
        self.session = requests.Session()      #保持连接池

    def get_articles(self, pages=10, limit=20):
        """获取文章列表"""
        for page in range(pages):
            params = {"limit": limit, "offset": page * limit}
            try:
                response = self.session.get(ARTICLE_API["index"], params=params)
                response.raise_for_status()
                yield from response.json().get("data", [])
            except requests.RequestException as e:
                logging.error(f"Fetch articles failed: {e}")

    def get_article_detail(self, article_id):
        """获取文章详情"""
        try:
            response = self.session.get(ARTICLE_API["detail"], params={"id": article_id})
            response.raise_for_status()
            return response.json().get("data", {}).get("body", "")
        except requests.RequestException as e:
            logging.error(f"Fetch article {article_id} detail failed: {e}")
            return ""

    def get_comments(self, article_id):
        """获取文章评论"""
        try:
            response = self.session.get(COMMENT_API, params={"article_id": article_id})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Fetch comments for {article_id} failed: {e}")
            return {"total": 0, "data": []}


class DataProcessor:
    """数据处理类"""

    def __init__(self, crawler, db):
        self.crawler = crawler
        self.db = db

    def process_articles(self, pages=10):
        """处理文章数据"""
        for article in self.crawler.get_articles(pages=pages):
            try:
                # 提取基础信息
                article_id = article["id"]
                title = article.get("title", "")
                likes = article.get("like_count", 0)
                author = article.get("author", {}).get("nickname", "")
                time = article.get("released_time", 0)

                # 获取并处理正文内容
                raw_content = self.crawler.get_article_detail(article_id)
                cleaned_content = BeautifulSoup(raw_content, "lxml").get_text()

                # 存储文章数据
                self.db.insert_article((
                    article_id,
                    title,
                    cleaned_content,
                    likes,
                    author,
                    time
                ))

                # 处理评论数据
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


def main():
    """主程序"""
    # 初始化组件
    db_handler = DatabaseHandler(DB_CONFIG)     #数据库初始化
    crawler = SSPAICrawler()                    #爬虫初始化
    processor = DataProcessor(crawler, db_handler)          #组合组件

    try:
        # 执行处理流程
        processor.process_articles(pages=10)
    finally:
        # 清理资源
        db_handler.close()


if __name__ == "__main__":
    main()