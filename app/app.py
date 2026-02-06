from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import Post, create_db_and_table, get_async_session
from app.images import imagekit
import tempfile
import os
import shutil


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_table()
    yield


fast_app = FastAPI(lifespan=lifespan)


@fast_app.post('/upload')
async def upload_file(file: UploadFile = File(...), caption: str = Form(''), session: AsyncSession = Depends(get_async_session)):

    temp_file_path = None

    try:
        # Temperary file to store the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

            # upload the image / video to imagekit
            upload_response = imagekit.files.upload(
                file=open(temp_file_path, 'rb'),
                file_name=file.filename
            )

            if upload_response.file_id and upload_response.url is not None:

                # CREATE POST OBJECT
                post = Post(
                    caption=caption,
                    url=upload_response.url,
                    file_type='video' if file.content_type.startswith(
                        'video/') else 'image',
                    file_name=upload_response.name
                )

                session.add(post)
                await session.commit()
                await session.refresh(post)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            file.file.close()


@fast_app.get('/feed')
async def get_feed(session: AsyncSession = Depends(get_async_session)):

    result = await session.execute(select(Post).order_by(Post.created_at.desc()))

    # extract the posts from results
    posts = [row[0] for row in result.all()]

    posts_data = []

    for post in posts:
        posts_data.append({
            'id': post.id,
            'caption': post.caption,
            'url': post.url,
            'file_type': post.file_type,
            'file_name': post.file_name,
            'created_at': post.created_at
        })

        return {'posts': posts_data}
