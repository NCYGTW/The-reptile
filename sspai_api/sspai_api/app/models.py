from sqlmodel import SQLModel, Field
from sqlalchemy import Text, VARCHAR, Column
from sqlalchemy.dialects.mysql import LONGTEXT
from pydantic import BaseModel
from typing import Optional

# SQLModel 数据模型定义
class ArticleBase(SQLModel):
    """文章模型的基类"""
    article_id: int = Field(index=True, unique=True)
    article_title: Optional[str] = Field(default=None, max_length=255)
    article_text: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    article_likes: int
    article_time: Optional[str] = Field(default=None)
    article_author: Optional[str] = Field(default=None, max_length=100)

class Article(ArticleBase, table=True):
    """为每篇入库的文章随机分配一个id"""
    id: Optional[int] = Field(default=None, primary_key=True)

class BestCommentBase(SQLModel):
    """评论模型的基类"""
    comment_id: int
    article_id: int = Field(index=True)  # 移除unique=True，一个文章可能有多条评论
    best_comment: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    comment_author: Optional[str] = Field(default=None, max_length=100)
    comment_time: Optional[str] = Field(default=None)

class BestComment(BestCommentBase, table=True):
    """为每个入库的模型随机分配一个id"""
    id: Optional[int] = Field(default=None, primary_key=True)

# Pydantic 模型，用于API响应
class ArticleResponse(ArticleBase):
    """在继承ArticleBase的基础上添加了id元素，规定用户查询库中文章时响应的信息格式"""
    id: int

class CommentResponse(BestCommentBase):
    """在继承CommentBase的基础上添加了id元素，规定用户查询库中评论时响应的信息格式"""
    id: int