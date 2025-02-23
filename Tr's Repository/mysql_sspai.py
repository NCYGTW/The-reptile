import requests
import pymysql
import cryptography
import mysql.connector

# 连接MySQL数据库
db = pymysql.connect(host = "localhost",
                     port = 3306,
                     user = "root",
                     passwd = "Tian1901",
                     database = "app",
                     charset = "utf8mb4")  #数据库名称
cursor = db.cursor()      #建立游标对象

# 在数据库中创建一个表
create_table_sql = """  
CREATE TABLE IF NOT EXISTS bestcomments(
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    best_comment TEXT,
    reply_count INT NOT NULL ,
    created_at TIMESTAMP , 
    UNIQUE (article_id , best_comment)
);
"""
cursor.execute(create_table_sql)   #在数据库中，执行创建一个表的任务
db.commit()      #将“创建一个表“的操作永久保存到数据库中

max_replies = 0
best_comment = None
best_comment_time = 0

for i in range(0, 2):
    h = 20 * i
    params = {
        'limit': '20',
        'offset': str(h),
    }
    response = requests.get('https://sspai.com/api/v1/article/index/page/get', params=params)
    data = response.json()

    for article in data['data']:
        article_id = article['id']
        params = {'article_id': str(article_id)}
        response = requests.get('https://sspai.com/api/v1/comment/user/article/hot/page/get', params=params)
        comments = response.json()

        if comments['total'] == 0:
            continue
        else:
            for comment in comments['data']:
                if 'reply' in comment and len(comment['reply']) > max_replies:
                    max_replies = len(comment['reply'])
                    best_comment = comment['comment']
                    best_comment_time = comment['created_at']
                elif 'reply' in comment and len(comment['reply']) == max_replies:
                    if comment['created_at'] > best_comment_time:
                        max_replies = len(comment['reply'])
                        best_comment = comment['comment']
                        best_comment_time = comment['created_at']

                insert_sql = """
                            INSERT IGNORE INTO bestcomments (article_id, best_comment, reply_count, created_at)
                            VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
                            """
                try:
                    cursor.execute(insert_sql, (article_id, best_comment, max_replies, best_comment_time))
                    db.commit()  # 同上
                    print("Data inserted successfully.")
                except mysql.connector.IntegrityError as e:
                    print("Duplicate data found. Operation aborted.")
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")

                # 重置变量
                max_replies = 0
                best_comment = None
                best_comment_time = 0

# 关闭数据库连接
cursor.close()
db.close()


