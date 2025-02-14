import requests
max_replies = 0
best_comment = None
for i in range(0,1000):
    h = 20 * i
    params = {
        'limit': '20',          #返回20条记录
        'offset': str(h),       #跳过前20*i条记录，以实现翻页功能
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
        for comment in comments['data'] :
            if 'reply' in comment and len(comment['reply']) > max_replies and comments['total']!=0:
                max_replies = len(comment['reply'])
                best_comment = comment['comment']
                best_comment_time = comment['created_at']
            elif 'reply' in comment and len(comment['reply']) == max_replies and comments['total']!=0:
                if comment['created_at'] > best_comment_time:
                    max_replies = len(comment['reply'])
                    best_comment = comment['comment']
                    best_comment_time = comment['created_at']
        print(f"Updated best comment with {max_replies} replies: {best_comment}")
        print([article_id])
        max_replies = -1



