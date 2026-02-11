from contextlib import asynccontextmanager
import uuid
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from app.users import current_active_user, fastapi_users
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import auth_user
from app.db import Post, User, create_db_and_table, get_async_session
from app.images import imagekit
import tempfile
import os
import shutil

from app.schemas import UserCreate, UserRead, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_table()
    yield


fast_app = FastAPI(lifespan=lifespan)


fast_app.include_router(fastapi_users.get_auth_router(auth_user), prefix='/auth/jwt', tags=['auth'])
    
fast_app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix='/auth', tags=['auth'])

fast_app.include_router(fastapi_users.get_reset_password_router(), prefix='/auth', tags=['auth'])

fast_app.include_router(fastapi_users.get_verify_router(UserRead), prefix='/auth', tags=['auth'])

fast_app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix='/users', tags=['users'])


@fast_app.post('/upload')
async def upload_file(file: UploadFile = File(...), caption: str = Form(''), session: AsyncSession = Depends(get_async_session) ,  user: User = Depends(current_active_user)):

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
                    user_id=user.id,
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


@fast_app.delete('/posts/{post_id}')
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):

    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))

        post = result.scalars().first()

        if not post:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail='post not found')

        await session.delete(post)
        await session.commit()

        return {'Success': True, 'message': 'Post deleted successfully'}

    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


