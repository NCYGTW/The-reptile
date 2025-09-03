#使用FastAPI构建API服务，SQLModel处理数据模型，Pydantic验证，uvicorn作为ASGI服务器
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict, Any
import logging
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# 导入其他模块
from models import Article, BestComment, ArticleResponse, CommentResponse
from database import create_db_and_tables, get_session, DatabaseHandler
from crawler import SSPAICrawler
from processor import DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 定时任务函数
def scheduled_crawl():
    """定时爬取数据的任务"""
    logging.info("开始定时爬取数据")
    try:
        # 创建新的会话
        session = next(get_session())
        crawler = SSPAICrawler()
        db_handler = DatabaseHandler(session)
        processor = DataProcessor(crawler, db_handler)
        processor.process_articles(pages=10)  # 每次爬取10页
        logging.info("定时爬取完成")
    except Exception as e:
        logging.error(f"定时爬取失败: {e}")
    finally:
        # 关闭会话
        session.close()

# FastAPI实例初始化
# 使用lifespan替代已弃用的on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_db_and_tables()
    logging.info("应用启动，创建数据库表完成")

    # 初始化调度器
    scheduler = BackgroundScheduler()
    # 添加定时任务：每小时执行一次
    scheduler.add_job(
        scheduled_crawl,
        trigger=IntervalTrigger(hours=1),
        id="hourly_crawl",
        replace_existing=True
    )
    # 启动调度器
    scheduler.start()
    logging.info("启动定时任务调度器，每小时爬取一次数据")

    # 应用启动时立即爬取一次
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, scheduled_crawl)

    yield

    # 关闭时清理资源
    scheduler.shutdown()
    logging.info("应用关闭，调度器已停止")

app = FastAPI(title="SSPAI 数据API", lifespan=lifespan)


# API 路由
@app.post("/crawl/{pages}", response_model=Dict[str, str])
def crawl_articles(pages: int, session: Session = Depends(get_session)):
    """爬取指定页数的文章"""
    try:
        crawler = SSPAICrawler()
        db_handler = DatabaseHandler(session)
        processor = DataProcessor(crawler, db_handler)
        processor.process_articles(pages=pages)
        return {"status": "success", "message": f"Processed {pages} pages of articles"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """获取文章列表"""
    articles = session.exec(select(Article).offset(skip).limit(limit)).all()
    return articles


@app.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, session: Session = Depends(get_session)):
    """获取单篇文章的数据"""
    article = session.exec(select(Article).where(Article.article_id == article_id)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/comments", response_model=List[CommentResponse])
def get_comments(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """获取文章的评论列表"""
    comments = session.exec(select(BestComment).offset(skip).limit(limit)).all()
    return comments


@app.get("/comments/{article_id}", response_model=CommentResponse)
def get_comment(article_id: int, session: Session = Depends(get_session)):
    """获取文章的最佳评论"""
    comment = session.exec(select(BestComment).where(BestComment.article_id == article_id)).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)