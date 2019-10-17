# coding=utf-8
import functools

import json

from flask import Blueprint, request
from pony.orm import *
from models import db, User, Comment, Blog, next_id
from apis import Page
from handlers import get_page_index
from handlers import cookie2user
from apis import APIValueError

bp = Blueprint('api', __name__, url_prefix='/api')


def table2Json(t):
    t = '[%s]' % t.rstrip().rstrip(',')
    t = json.loads(t)
    return t


@bp.route('/blogs', methods=['GET'])
def api_blogs():
    page = request.args.get('page', '1')
    page_index = get_page_index(page)
    with db_session:
        num = len(select(b for b in Blog)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    b = ''
    with db_session:
        blogs = select(b for b in Blog).order_by(desc(Blog.created_at))[p.offset: p.limit+p.offset]
        for blog in blogs:
            b = b + '{"id": "%s", "user_id": "%s", "user_name": "%s", "user_image": "%s", "name": "%s", "summary": "%s", "content": "%s", "created_at": %s}, ' \
            % (blog.id, blog.user_id, blog.user_name, blog.user_image, blog.name, blog.summary, blog.content, blog.created_at)
    b = table2Json(b)
    p = json.loads(str(p))
    return dict(page=p, blogs=b)

@bp.route('/users', methods=['GET'])
def api_users():
    page = request.args.get('page', '1')
    page_index = get_page_index(page)
    with db_session:
        num = len(select(u for u in User)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    u = ''
    with db_session:
        users = select(u for u in User).order_by(desc(User.created_at))[p.offset: p.limit+p.offset]
        for user in users:
            u = u + '{"id": "%s", "email": "%s", "passwd": "******", "admin": "%s", "name": "%s", "image": "%s", "created_at": %s}, ' \
                % (user.id, user.email, user.admin, user.name, user.image, user.created_at)
    u = table2Json(u)
    p = json.loads(str(p))
    return dict(page=p, users=u)


@bp.route('/comments', methods=['GET'])
def api_comments(*, page='1'):
    page_index = get_page_index(page)
    with db_session:
        num = len(select(c for c in Comment)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    c = ''
    with db_session:
        comments = select(c for c in Comment).order_by(desc(Comment.created_at))[p.offset: p.limit+p.offset]
        for comment in comments:
            c = c + '{"id": "%s", "blog_id": "%s", "user_id": "%s", "user_name": "%s", "user_image": "%s", "content": "%s", "created_at": %s}, ' \
                % (comment.id, comment.blog_id, comment.user_id, comment.user_name, comment.user_image, comment.content, comment.created_at)
    c = table2Json(c)
    p = json.loads(str(p))
    return dict(page=p, comments=c)


@bp.route('/blogs/<id>', methods=['GET'])
@db_session
def api_blog(id):
    blog = Blog.get(id=id)
    return blog.to_dict()


@bp.route('/blogs/<id>/comments', methods=['POST'])
@db_session
def api_create_comment(id):
    user = user = cookie2user()
    if user is None:
        raise APIPermissionError('Please signin first.')
    content = request.json['content']
    if not content or not content.strip():
        raise APIValueError('content')
    blog = Blog.get(id=id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    return comment.to_dict()

