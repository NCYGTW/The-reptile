"""
SSPAI 数据库建表语句
包含文章表和评论表的创建语句
"""

# 创建数据库
CREATE_DATABASE = """
CREATE DATABASE IF NOT EXISTS abcd 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
"""

# 创建文章表
CREATE_ARTICLE_TABLE = """
CREATE TABLE IF NOT EXISTS article (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL UNIQUE,
    article_title VARCHAR(255),
    article_text LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    article_likes INT NOT NULL DEFAULT 0,
    article_time VARCHAR(50),
    article_author VARCHAR(100),
    INDEX idx_article_id (article_id)
) ENGINE=InnoDB 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
"""

# 创建评论表
CREATE_COMMENT_TABLE = """
CREATE TABLE IF NOT EXISTS bestcomment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT NOT NULL,
    article_id INT NOT NULL,
    best_comment LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    comment_author VARCHAR(100),
    comment_time VARCHAR(50),
    INDEX idx_article_id (article_id),
    INDEX idx_comment_id (comment_id)
) ENGINE=InnoDB 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
"""

# 修改表结构的SQL语句
ALTER_ARTICLE_TABLE = """
ALTER TABLE article 
MODIFY COLUMN article_text LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

ALTER_COMMENT_TABLE = """
ALTER TABLE bestcomment 
MODIFY COLUMN best_comment LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

# 修改表字符集
ALTER_ARTICLE_CHARSET = """
ALTER TABLE article 
CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

ALTER_COMMENT_CHARSET = """
ALTER TABLE bestcomment 
CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

# 查看表结构
DESCRIBE_ARTICLE = "DESCRIBE article;"
DESCRIBE_COMMENT = "DESCRIBE bestcomment;"

# 删除表
DROP_ARTICLE_TABLE = "DROP TABLE IF EXISTS article;"
DROP_COMMENT_TABLE = "DROP TABLE IF EXISTS bestcomment;"

# 清空表数据
TRUNCATE_ARTICLE_TABLE = "TRUNCATE TABLE article;"
TRUNCATE_COMMENT_TABLE = "TRUNCATE TABLE bestcomment;"

# 查看表中数据量
COUNT_ARTICLES = "SELECT COUNT(*) as article_count FROM article;"
COUNT_COMMENTS = "SELECT COUNT(*) as comment_count FROM bestcomment;"

# 查看表索引
SHOW_INDEX_ARTICLE = "SHOW INDEX FROM article;"
SHOW_INDEX_COMMENT = "SHOW INDEX FROM bestcomment;"

if __name__ == "__main__":
    print("SSPAI 数据库建表语句")
    print("=" * 50)
    print("1. 创建数据库:")
    print(CREATE_DATABASE)
    print("\n2. 创建文章表:")
    print(CREATE_ARTICLE_TABLE)
    print("\n3. 创建评论表:")
    print(CREATE_COMMENT_TABLE)
    print("\n4. 修改表结构:")
    print(ALTER_ARTICLE_TABLE)
    print(ALTER_COMMENT_TABLE)
    print("\n5. 修改表字符集:")
    print(ALTER_ARTICLE_CHARSET)
    print(ALTER_COMMENT_CHARSET)
