#
# Database access functions for the web forum.
# 

import time
import psycopg2
import bleach
## Database connection

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    
    DBconn = psycopg2.connect("dbname=forum")
    cur = DBconn.cursor()

    cur.execute("SELECT time,content FROM posts ORDER BY time DESC")
    rows = cur.fetchall()
    posts = [{'content': str(row[1]), 'time': str(row[0])} for row in rows]
    DBconn.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    content_clean = bleach.clean(content)
    DBconn = psycopg2.connect("dbname=forum")
    cur = DBconn.cursor()
    cur.execute("INSERT INTO posts (content) VALUES (%s)", (content_clean,))
    DBconn.commit()
    DBconn.close()
