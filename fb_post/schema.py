import graphene
from graphene import ObjectType, Schema, Mutation
from fb_post.models import User, Group, Post, Comment, React


class UserType(ObjectType):
    user_id = graphene.ID()
    name = graphene.String()
    profile_pic = graphene.String()


class GroupType(ObjectType):
    id = graphene.ID()
    name = graphene.String()
    members = graphene.List(UserType)


class ReactType(ObjectType):
    reaction = graphene.String()
    reacted_at = graphene.DateTime()
    reacted_by = graphene.Field(UserType)
    post = graphene.Field('fb_post.schema.PostType')
    comment = graphene.Field('fb_post.schema.CommentType')


class CommentType(ObjectType):
    comment_id = graphene.ID()
    content = graphene.String()
    commented_at = graphene.DateTime()
    commented_by = graphene.Field(UserType)
    post = graphene.Field('fb_post.schema.PostType')
    reply = graphene.Field('fb_post.schema.CommentType')
    reactions = graphene.List(ReactType)
    replies = graphene.List('fb_post.schema.CommentType')

    def resolve_reactions(self, info):
        return React.objects.filter(comment=self)

    def resolve_replies(self, info):
        return Comment.objects.filter(reply=self)


class PostType(ObjectType):
    post_id = graphene.ID()
    content = graphene.String()
    posted_at = graphene.DateTime()
    posted_by = graphene.Field(UserType)
    group = graphene.Field(GroupType)
    comments = graphene.List(CommentType)
    reactions = graphene.List(ReactType)

    def resolve_comments(self, info):
        return Comment.objects.filter(post=self)

    def resolve_reactions(self, info):
        return React.objects.filter(post=self)


class Query(ObjectType):
    all_users = graphene.List(UserType)
    all_posts = graphene.List(PostType)
    all_comments = graphene.List(CommentType)
    all_reacts = graphene.List(ReactType)
    all_groups = graphene.List(GroupType)
    all_posts_by_user = graphene.List(PostType, user_id=graphene.Int(required=True))
    all_comments_by_post = graphene.List(CommentType, post_id=graphene.Int(required=True))
    all_reacts_by_post = graphene.List(ReactType, post_id=graphene.Int(required=True))
    posts_by_user_with_comments_and_reactions = graphene.List(PostType, user_id=graphene.Int(required=True))

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

    def resolve_all_posts_by_user(self, info, user_id):
        return Post.objects.filter(posted_by=user_id)

    def resolve_all_comments_by_post(self, info, post_id):
        return Comment.objects.filter(post=post_id)

    def resolve_all_reacts_by_post(self, info, post_id):
        return React.objects.filter(post=post_id)

    def resolve_posts_by_user_with_comments_and_reactions(self, info, user_id):
        return Post.objects.filter(posted_by=user_id).prefetch_related('commenter', 'reacted_to_post')


# User Mutations
class CreateUser(Mutation):
    class Arguments:
        name = graphene.String(required=True)
        profile_pic = graphene.String(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, name, profile_pic):
        user = User.objects.create(
            name=name,
            profile_pic=profile_pic
        )
        return CreateUser(user=user)


class UpdateUser(Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        name = graphene.String()
        profile_pic = graphene.String()

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, user_id, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            user.save()
            return UpdateUser(user=user)
        except User.DoesNotExist:
            raise Exception("User not found")


class DeleteUser(Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            user.delete()
            return DeleteUser(success=True)
        except User.DoesNotExist:
            raise Exception("User not found")


class UserMutations(ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()


class Mutation(UserMutations, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
