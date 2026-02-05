from fastapi import FastAPI , HTTPException
from app.schemas import Post


fast_app = FastAPI()

text_posts = {1: {'title': '48hours',
                  'caption': 'How to change your life in 48 hours'},
              2: {'title': 'Nicosia',
                  'caption': 'The only shared capital'}}


@fast_app.get('/')
def home_page():
    return {'hello':'world'}

@fast_app.get('/post')
def get_posts():
    return text_posts

@fast_app.get('/post{id}')
def get_post_by_id(id:int):
    return text_posts[id]

@fast_app.post('/create')
def create_post(post: Post):
    new_id = max(text_posts , default=0) + 1
    text_posts[new_id] = {'title':post.title , 'caption':post.caption}
    return text_posts[new_id]

@fast_app.delete('/post')
def delete_post(id:int):
    del text_posts[id]
    return {'message':'post deleted'}


