#coding: utf-8
from flask import Flask, request, g
from flask_restful import Resource, Api
from flask_restful import abort
from flask_restful import reqparse


app = Flask(__name__)
api = Api(app)
app.debug = True

from peewee import * 

#创建数据库表
db = SqliteDatabase('posts.db')

class Post(Model):
    title = CharField(unique=True)
    content = TextField()

    class Meta:
        database = db


#g.db 表示global的属性，而且是单例模式的
#在每个请求前连接数据库，请求结束后关闭数据库连接
@app.before_request
def before_request():
    g.db = db
    g.db.connect()

@app.after_request
def before_request(response):
    g.db.close()
    return response


def abort_if_post_doesnt_exist(post_id):
    post_id = int(post_id)
    try: 
        Post.get(Post.id == post_id)
    except PostDoesNotExist:
        abort(404, message="POSTS doesn't exist")


parser = reqparse.RequestParser()
parser.add_argument('post', type=int)

class PostResource(Resource): 
    # /posts/1 GET
    def get(self, post_id):
        post_id = int(post_id)
        abort_if_post_doesnt_exist(post_id)
        
        post = Post.get(Post.id == post_id)
        return {'title': post.title, 'content': post.content}

    # /posts/1 DELETE
    def delete(self, post_id):
        post_id = int(post_id)
        abort_if_post_doesnt_exist(post_id)
        rows = Post.get(Post.id == post_id).delete_instance()
        return rows, 204

    # /posts/1 PUT
    def put(self, post_id):
        json_data = request.get_json(force=True)
        post_id = int(post_id)
        post = {'title': json_data['title'], 'content': json_data['content']}
        Post.update(title=json_data['title'], content=json_data['content']).where(Post.id == post_id).execute()
       
        return post, 201

class PostList(Resource):
    # /posts GET
    def get(self):
    	posts = []
        raw_posts = Post.select()
    	for post in raw_posts:
    		if post:
    			new_post = {}    			
                new_post['url'] = '/posts/' + str(post.id)    			
                new_post['title'] = post.title
                posts.append(new_post)
    	return posts


    # /posts POST
    def post(self):
        json_data = request.get_json(force=True)
        print json_data
        try:
            post = Post.create(title=json_data['title'], content=json_data['content'])          
            return post.id, 201
        except IntegrityError:
            return {'message': 'the title is already token'}, 401

api.add_resource(PostList, '/posts')
api.add_resource(PostResource, '/posts/<post_id>')


if __name__ == '__main__':
    app.run(debug=True)
