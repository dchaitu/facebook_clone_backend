import graphene
from graphene import ObjectType, Schema
from graphene_django import DjangoObjectType, DjangoListField

from fb_post.models import User, Group, Post, Comment, React


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = '__all__'


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = '__all__'


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = '__all__'

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = '__all__'

class ReactType(DjangoObjectType):
    class Meta:
        model = React
        fields = '__all__'


class Query(ObjectType):

    # all_users = DjangoListField(UserType)
    all_users = graphene.List(UserType)
    all_posts = graphene.List(PostType)
    all_comments = graphene.List(CommentType)
    all_reacts = graphene.List(ReactType)
    all_groups = graphene.List(GroupType)

    user = graphene.Field(UserType, user_id=graphene.Int(required=True))
    def resolve_all_users(self, info):
        return User.objects.all()

    def resolve_user(self, info, user_id):
        return User.objects.get(user_id=user_id)

    def resolve_all_posts(self, info):
        return Post.objects.all()

    def resolve_all_comments(self, info):
        return Comment.objects.all()

    def resolve_all_reacts(self, info):
        return React.objects.all()

schema = Schema(query=Query)