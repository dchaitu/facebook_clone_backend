from django.db.models import Q, Count, F
from fb_post.models import User, Post, Comment, React
from fb_post.utils.exceptions import InvalidUserException, InvalidCommentException, \
    InvalidPostException, InvalidCommentContent, InvalidReplyContent, InvalidReactionTypeException, \
    UserCannotDeletePostException
from fb_post.constants.enum import ReactionType
from datetime import datetime


def create_post(user_id, post_content,group_id):
    """
    :returns: post_id
    """
    if len(post_content) == 0:
        raise InvalidPostException("Post is empty")
    try:
        user = User.objects.get(user_id=user_id)
        post = Post.objects.create(posted_by=user, content=post_content,
                                   posted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   ,group_id=group_id)
        post.save()

        return post



    except User.DoesNotExist:
        raise InvalidUserException


def create_comment(user_id, post_id, comment_content):
    """
    :returns: comment_id
    """
    if len(comment_content) == 0:
        raise InvalidCommentContent("Comment id is not defined")

    try:
        user = User.objects.get(user_id=user_id)
        post = Post.objects.get(post_id=post_id)
        post.save()
        comment = Comment.objects.create(content=comment_content,
                                         commented_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                         commented_by=user,
                                         post=post)

        comment.save()

        return comment

    except Post.DoesNotExist:
        raise InvalidPostException("Post id not in database")

    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")


def reply_to_comment(user_id, comment_id, reply_content):
    """
    :returns: comment_id
    """
    if len(reply_content) == 0:
        raise InvalidReplyContent

    try:
        user = User.objects.get(user_id=user_id)
        comment = Comment.objects.get(comment_id=comment_id)
        reply = Comment.objects.create(commented_by=user, content=reply_content, reply=comment,
                                       commented_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        reply.save()

        return reply.comment_id

    # Additionally , if the given comment_id corresponds to a 'reply' instead of a direct comment to a post, then a reply should be created to the comment

    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")

    except Comment.DoesNotExist:
        raise InvalidCommentException("Comment id is not defined")


def react_to_post(user_id, post_id, reaction_type):
    """
    """
    if reaction_type not in [ReactionType.WOW.value, ReactionType.HA.value, ReactionType.UP.value,
                             ReactionType.ANGRY.value,
                             ReactionType.LIT.value, ReactionType.DOWN.value, ReactionType.SAD.value,
                             ReactionType.LOVE.value]:
        raise InvalidReactionTypeException("Reaction Type is not defined")
    try:
        user = User.objects.get(user_id=user_id)
        if not user:
            raise InvalidUserException
        post = Post.objects.get(post_id=post_id)
        if not post:
            raise InvalidPostException
        reacted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        already_reacted = React.objects.filter(reacted_by=user_id, post=post)
        if already_reacted:
            already_reacted.delete()
        react = React.objects.create(reacted_at=reacted_time, reacted_by=user, post=post, reaction=reaction_type)
        react.save()

    except Post.DoesNotExist:
        raise InvalidPostException("Post id is not defined")

    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")


def react_to_comment(user_id, comment_id, reaction_type):
    """
    """
    if reaction_type not in [ReactionType.WOW.value, ReactionType.HA.value, ReactionType.UP.value,
                             ReactionType.ANGRY.value,
                             ReactionType.LIT.value, ReactionType.DOWN.value, ReactionType.SAD.value,
                             ReactionType.LOVE.value]:
        raise InvalidReactionTypeException("Reaction Type is not defined")

    try:
        user = User.objects.get(user_id=user_id)
        comment = Comment.objects.get(comment_id=comment_id)

        reaction_exists = React.objects.get(comment=comment, reacted_by=user)
        if reaction_exists.reaction == reaction_type:
            reaction_exists.delete()
        elif reaction_exists.reaction != reaction_type:
            reaction_exists.reaction = reaction_type
            reaction_exists.reacted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reaction_exists.save()
        else:
            React.objects.create(reaction=reaction_type, comment=comment, reacted_by=user,
                                 reacted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")


def get_total_reaction_count():
    r = React.objects.count()
    return r


def get_reaction_metrics(post_id):
    """Return total count for each reaction type"""
    try:
        post = Post.objects.get(post_id=post_id)
        love = Q(reaction=ReactionType.LOVE.value)
        lit = Q(reaction=ReactionType.LIT.value)
        up = Q(reaction=ReactionType.UP.value)
        down = Q(reaction=ReactionType.DOWN.value)
        wow = Q(reaction=ReactionType.WOW.value)
        sad = Q(reaction=ReactionType.SAD.value)
        angry = Q(reaction=ReactionType.ANGRY.value)
        post = Q(post=post)

        metrics = {"LOVE": React.objects.filter(post & love).count(),
             "LIT": React.objects.filter(post & lit).count(),
             "UP": React.objects.filter(post & up).count(),
             "DOWN": React.objects.filter(post & down).count(),
             "WOW": React.objects.filter(post & wow).count(),
             "SAD": React.objects.filter(post & sad).count(),
             "ANGRY": React.objects.filter(post & angry).count()}

        return metrics
    except Post.DoesNotExist:
        raise InvalidPostException("post id is defined")


def delete_post(user_id, post_id):
    """
    """
    try:
        user = User.objects.get(user_id=user_id)

        post = Post.objects.get(pk=post_id)

        if post.posted_by == user:
            post.delete()
            print(f"post No {post_id} deleted and comments and reactions to it also deleted")
        else:
            raise UserCannotDeletePostException


    # InvalidPostException
    except Post.DoesNotExist:
        raise InvalidPostException("Post is not created by user")
    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")


# Need to check
def get_posts_with_more_positive_reactions():
    """
    """
    positive = [ReactionType.WOW.value, ReactionType.LOVE.value, ReactionType.LIT.value, ReactionType.HA.value,
                ReactionType.UP.value]
    negative = [ReactionType.DOWN.value, ReactionType.ANGRY.value, ReactionType.SAD.value]
    posr = Count('reacted_to_post', filter=Q(reacted_to_post__reaction__in=positive))
    negr = Count('reacted_to_post', filter=Q(reacted_to_post__reaction__in=negative))
    posts_with_more_positive_reactions = Post.objects.annotate(postive_count=posr, negative_count=negr).filter(
        postive_count__gt=F('negative_count'))

    return list(posts_with_more_positive_reactions)


# check

def get_posts_reacted_by_user(user_id):
    """
    :returns: list of post ids
    """
    try:
        user = User.objects.get(user_id=user_id)
        reacted_posts = React.objects.filter(reacted_by=user)
        post_ids = Post.objects.filter(post_id__in=reacted_posts).values('post_id')

        return list(post_ids)

    except User.DoesNotExist:
        raise InvalidUserException


def get_reactions_to_post(post_id):
    """
    :returns: [
        {"user_id": 1, "name": "iB Cricket", "profile_pic": "", "reaction": "LIKE"},
        ...
    ]
    """
    try:
        post = Post.objects.get(post_id=post_id)
        reactions = React.objects.filter(post=post).select_related('post__posted_by')

        react_list = []

        for r in reactions:
            react_dict = {}
            react_dict.update(r.reacted_by.get_user_dict())
            react_dict['reaction'] = r.reaction
            react_list.append(react_dict)

        return react_list

    except (Post.DoesNotExist, Post.MultipleObjectsReturned):
        raise InvalidPostException


# Exceptions not working properly
"""
    :returns: {
        "post_id": 1,
        "posted_by": {
            "name": "iB Cricket",
            "user_id": 1,
            "profile_pic": "https://dummy.url.com/pic.png"
        },
        "posted_at": "2019-05-21 20:21:46.810366"
        "post_content": "Write Something here...",
        "reactions": {
            "count": 10,
            "type": ["HAHA", "WOW"]
        },
        "comments": [
            {
                "comment_id": 1
                "commenter": {
                    "user_id": 2,
                    "name": "Yuri",
                    "profile_pic": "https://dummy.url.com/pic.png"
                },
                "commented_at": "2019-05-21 20:22:46.810366",
                "comment_content": "Nice game...",
                "reactions": {
                    "count": 1,
                    "type": ["LIKE"]
                },
                "replies_count": 1,
                "replies": [{
                    "comment_id": 2
                    "commenter": {
                        "user_id": 1,
                        "name": "iB Cricket",
                        "profile_pic": "https://dummy.url.com/pic.png"
                    },
                    "commented_at": "2019-05-21 20:22:46.810366",
                    "comment_content": "Thanks...",
                    "reactions": {
                        "count": 1,
                        "type": ["LIKE"]
                    },
                }]
            },
            ...
        ],
        "comments_count": 3,
    }
    """


def get_post(post_id):
    try:

        post = Post.objects.get(pk=post_id)
        reactions = React.objects.filter(post=post).select_related('post','reacted_by','comment')
        comments = Comment.objects.filter(post=post).select_related('commented_by')
        reacted_to_comment = React.objects.filter(comment__in=comments).select_related('comment')
        all_comments = []
        post_obj = {}
        post_obj.update(post.get_post_dict())
        all_types = []
        for react in reactions:
            if react.reaction not in all_types:
                all_types.append(react.reaction)
        post_obj.update({"reactions": {"count": reactions.count(), "type": all_types}})
        del post_obj['group']
        for comment in comments:
            comment_obj = {}
            comment_obj.update(comment.get_comment_dict())
            reaction_type = []

            for react in reacted_to_comment:
                if react.reaction not in reaction_type:
                    reaction_type.append(react.reaction)
            comment_obj.update({"reactions": {"count": reacted_to_comment.count(), "type": reaction_type}})
            replies = Comment.objects.filter(reply=comment)
            reaction_to_reply = React.objects.filter(comment__in=replies)
            reply_comments = []
            reply_reaction_type = []
            for y in replies:
                y = y.get_comment_dict()
                y.update({"reactions": {"count": reaction_to_reply.count(), "type": reply_reaction_type}})
                reply_comments.append(y)
            comment_obj.update({"replies": reply_comments})

            for react in reaction_to_reply:
                if react.reaction not in reply_reaction_type:
                    reply_reaction_type.append(react.reaction)

            all_comments.append(comment_obj)

        post_obj.update({"comments": all_comments})
        return post_obj
    except Post.DoesNotExist:
        raise InvalidPostException("post id doesn't exist")


def get_user_posts(user_id):
    """
    Explanation: Return a list of responses similar to get_post
    """
    posts = Post.objects.filter(posted_by=user_id)
    return posts


def get_replies_for_comment(comment_id):
    """
    :returns: [{
        "comment_id": 2
        "commenter": {
            "user_id": 1,
            "name": "iB Cricket",
            "profile_pic": "https://dummy.url.com/pic.png"
        },
        "commented_at": "2019-05-21 20:22:46.810366",
        "comment_content": "Thanks...",
    }]
    """
    replies = []
    try:

        comment = Comment.objects.get(pk=comment_id)
        reply = Comment.objects.filter(reply=comment)
        for y in reply:
            replies.append(y.get_comment_dict())
        return replies

    except Comment.DoesNotExist:
        raise InvalidCommentException("Comment is not created")
