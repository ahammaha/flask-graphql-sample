from flask import Flask
from config import Config
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.debug = True
# instantiate database object
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model):
	__tablename__ = 'users'
	uuid = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(256), index=True, unique=True)

	def __repr__(self):
		return '<User %r>' % self.username

class UserObject(SQLAlchemyObjectType):
   class Meta:
       model = User

'''
query{
  users{
    uuid
    username
  }
}
'''
class Query(graphene.ObjectType):
    users = graphene.List(UserObject)

    def resolve_users(self, info, **kwargs):
        return db.session.query(User)

'''
mutation{
  createUser(uuid:1, username:"maha"){
    uuid
    username
  }
}
'''
class CreateUser(graphene.Mutation):
    uuid=graphene.Int()
    username=graphene.String()
    class Arguments:
        uuid = graphene.Int()
        username = graphene.String()

    def mutate(self, info, uuid, username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            user=User(uuid=uuid, username=username)
            db.session.add(user)
            db.session.commit()
        return CreateUser(uuid=user.uuid, username=user.username)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)