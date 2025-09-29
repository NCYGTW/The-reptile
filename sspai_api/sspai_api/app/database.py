from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import logging
import os

# 从环境变量获取数据库连接信息，如果没有则使用默认值
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database.db")

# 创建引擎（负责管理和数据库的连接，把程序里的操作转化成SQL命令，执行并返回结果给程序）
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """自动根据元数据在数据库中建表"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """数据库会话依赖项"""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            session.close()

class DatabaseHandler:
    """数据库操作类 """

    def __init__(self, session: Session):
        self.session = session

    def insert_article(self, data: tuple):
        """插入文章数据"""
        from app.models import Article
        from sqlmodel import select
        
        article_id, title, content, likes, author, time = data

        statement = select(Article).where(Article.article_id == article_id)
        existing = self.session.exec(statement).first()

        if existing:
            logging.warning(f"Duplicate article {article_id} skipped")
            return

        article = Article(
            article_id=article_id,
            article_title=title,
            article_text=content,
            article_likes=likes,
            article_author=author,
            article_time=time
        )

        try:
            self.session.add(article)
            self.session.commit()
            self.session.refresh(article)
            logging.info(f"Article {article_id} inserted successfully")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Insert article error: {e}")

    def insert_comment(self, data: tuple):
        """插入评论数据"""
        from app.models import BestComment
        from sqlmodel import select
        
        comment_id, article_id, comment, author, time = data

        statement = select(BestComment).where(BestComment.article_id == article_id)
        existing = self.session.exec(statement).first()

        if existing:
            logging.warning(f"Duplicate comment for article {article_id} skipped")
            return

        comment_obj = BestComment(
            comment_id=comment_id,
            article_id=article_id,
            best_comment=comment,
            comment_author=author,
            comment_time=time
        )

        try:
            self.session.add(comment_obj)
            self.session.commit()
            self.session.refresh(comment_obj)
            logging.info(f"Comment for article {article_id} inserted successfully")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Insert comment error: {e}")