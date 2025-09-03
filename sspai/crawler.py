import requests
import logging

# API配置
ARTICLE_API = {
    "index": "https://sspai.com/api/v1/article/index/page/get",
    "detail": "https://sspai.com/api/v1/article/info/get"
}
COMMENT_API = "https://sspai.com/api/v1/comment/user/article/hot/page/get"

class SSPAICrawler:
    """请求与获取类"""

    def __init__(self):
        self.session = requests.Session()

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