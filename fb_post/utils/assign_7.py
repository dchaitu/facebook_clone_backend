from fb_post.models import User, Post, Comment, React, Group, Membership
from datetime import datetime

from fb_post.utils.exceptions import InvalidUserException, UserNotInGroupException, UserIsNotAdminException, \
    InvalidGroupNameException, \
    InvalidMemberException, \
    InvalidGroupException


def create_group(user_id, name, member_ids):
    if len(name)==0:
        raise InvalidGroupNameException("Game doesn't have name")

    try:
        admin = User.objects.get(user_id=user_id)
        group = Group.objects.create(name=name)
        users = User.objects.filter(user_id__in=member_ids)
        group.members.add(*users)
        group.save()
        m = Membership.objects.get(group=group, member=admin)
        m.is_admin = True
        m.save()
        return group.id

    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")

    except Membership.DoesNotExist:
        raise InvalidMemberException("Members are not present in db")


def add_member_to_group(user_id, new_member_id, group_id):
    try:

        member = User.objects.get(user_id=new_member_id)
        group = Group.objects.get(id=group_id)
        group.members.get(user_id=user_id)
        m = Membership.objects.get(group=group, member__user_id=user_id)
        check_admin = m.is_admin
        if check_admin == False:
            raise UserIsNotAdminException
        else:
            if member not in group.members.all():
                group.members.add(member)


    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")

    except (Group.DoesNotExist, Group.MultipleObjectsReturned):
        raise InvalidGroupException("Game doesn't have name")

    except User.DoesNotExist:
        raise InvalidMemberException("Members are not present in db")

    except Group.DoesNotExist:
        raise UserNotInGroupException("User not in group")

    except (PermissionError, Membership.MultipleObjectsReturned):
        raise UserIsNotAdminException("User is not an admin")


def remove_member_from_group(user_id, member_id, group_id):
    try:
        member = User.objects.get(user_id=member_id)
        group = Group.objects.get(id=group_id)
        m = Membership.objects.get(group=group, member__user_id=user_id)
        check_admin = m.is_admin
        if check_admin == False:
            raise UserIsNotAdminException
        else:
            if member in group.members.all():
                group.members.remove(member)
            else:
                raise InvalidMemberException


    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")

    except InvalidGroupNameException:
        print("Game doesn't have name")

    except User.DoesNotExist:
        raise InvalidMemberException("Members are not present in db")

    except UserIsNotAdminException:
        print("User is not an admin")


# should make the given member_id as group admin. If the member_id already an admin to the group, then do nothing.
def make_member_as_admin(user_id, member_id, group_id):
    try:
        user = User.objects.get(user_id=user_id)
        group = Group.objects.get(id=group_id)
        group.members.filter(user_id=user_id)
        u = Membership.objects.get(group=group, member__user_id=user_id)
        check_admin = u.is_admin
        if check_admin == False:
            raise UserIsNotAdminException
        else:
            m = Membership.objects.get(group=group, member__user_id=member_id)
            if m.is_admin == False:
                m.is_admin = True
            m.save()


    except InvalidUserException:
        raise InvalidUserException("User id is not defined")

    except Group.DoesNotExist:
        raise InvalidGroupException("Group doesn't exists")

    except User.DoesNotExist:
        raise InvalidMemberException("Members are not present in db")

    except (User.DoesNotExist, Group.DoesNotExist):
        raise UserNotInGroupException("User not in group")


def create_post(user_id, post_content, group_id=None):
    """
    :returns: post_id
    """
    try:
        user = User.objects.get(user_id=user_id)
        group = Group.objects.get(pk=group_id)
        m = Membership.objects.get(group=group, member__user_id=user_id)
        post = Post.objects.create(content=post_content, posted_at=datetime.now().strftime("%Y-%m-%d"), posted_by=user,
                                   group=group)

        group.save()
        return post.post_id
    except User.DoesNotExist:
        raise InvalidUserException("User id is not defined")

    except Group.DoesNotExist:
        raise InvalidGroupException("Game doesn't have name")

    except User.DoesNotExist:
        raise InvalidMemberException("Members are not present in db")

    except UserIsNotAdminException:
        print("User is not an admin")


def get_group_feed(user_id, group_id, offset, limit):
    """
    :return: [
    {
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
    ]
    """
    all_posts = []
    user = User.objects.get(user_id=user_id)
    group = Group.objects.get(pk=group_id)
    if user in group.members.all():
        posts = Post.objects.filter(posted_by=user)

        for post in posts:
            post_obj = {}
            post_obj.update(post.get_post_dict())
            del post_obj['group']
            react_obj = {}

            reactions = React.objects.filter(post=post)

            all_types = []
            for react in reactions:
                if react.reaction not in all_types:
                    all_types.append(react.reaction)

            react_obj.update({"reactions": {"count": reactions.count(), "type": all_types}})
            comments = Comment.objects.filter(post=post)
            comments_count = Comment.objects.filter(post=post).count()
            all_comments = []

            for comment in comments:
                comment_obj = {}
                comment_obj.update(comment.get_comment_dict())
                comment_react = React.objects.filter(comment = comment)
                react_comment = []
                reply_comments = []
                reply_reaction_type = []
                replies = Comment.objects.filter(reply=comment)
                reaction_to_reply = React.objects.filter(comment__in=replies)
                for y in replies:
                    y = y.get_comment_dict()
                    y.update({"reactions": {"count": reaction_to_reply.count(), "type": reply_reaction_type}})
                    reply_comments.append(y)
                comment_obj.update({"replies": reply_comments})
                for react in comment_react:
                    if react.reaction not in react_comment:
                        react_comment.append(react.reaction)
                comment_obj.update({"reactions": {
                    "count": comment_react.count(),
                    "type": react_comment
                }})
                all_comments.append(comment_obj)

            react_obj.update({"comments": all_comments})
            react_obj.update({"comments_count": comments_count})
            post_obj.update(react_obj)
            all_posts.append(post_obj)
    return all_posts[offset:offset + limit]


def get_posts_with_more_comments_than_reactions():
    """
    :returns: list of post_ids
    """
    all_posts = []
    posts = Post.objects.all()
    for post in posts:
        comment_count = (Comment.objects.filter(post=post).count())
        react_count = React.objects.filter(post=post).count()
        if comment_count > react_count:
            all_posts.append(post.post_id)

    return all_posts


def get_silent_group_members(group_id):
    """
    """
    group = Group.objects.get(id=group_id)
    users = group.members.all()
    silent_users = []
    for user in users:
        if Post.objects.filter(posted_by=user).count() == 0:
            silent_users.append(user)

    return silent_users


def get_user_posts(user_id):


    try:
        user = User.objects.get(user_id=user_id)
        posts = Post.objects.filter(posted_by=user)
        all_posts = []
        for post in posts:
            post_obj = {}
            post_obj.update(post.get_post_dict())
            reactions = React.objects.filter(post=post)
            all_types = []
            for react in reactions:
                if react.reaction not in all_types:
                    all_types.append(react.reaction)

            post_obj.update({"reactions": {"count": reactions.count(), "type": all_types}})
            comments = Comment.objects.filter(post=post)
            comments_count = Comment.objects.filter(post=post).count()
            all_comments = []
            for comment in comments:
                comment_obj = {}
                all_replies = []
                replies = Comment.objects.filter(reply__comment_id=comment.comment_id)
                replies_count = Comment.objects.filter(reply__comment_id=comment.comment_id).count()
                for reply in replies:
                    reply_obj = {}
                    reply_obj.update(reply.get_comment_dict())
                    reply_reactions = React.objects.filter(comment=reply)
                    all_reply_types = []
                    for react in reply_reactions:
                        all_reply_types.append(react.reaction)
                    reply_obj.update({"reactions": {"count": reactions.count(), "type": all_types}})
                    all_replies.append(reply_obj)
                comment_obj.update(comment.get_comment_dict())
                comment_obj.update({"replies_count": replies_count, "replies": all_replies})

                all_comments.append(comment_obj)

            post_obj.update({"comments": all_comments})
            post_obj.update({"comments_count": comments_count})
            all_posts.append(post_obj)
        return all_posts
    except:
        print("Invalid")
    """
    :return: [
    {
        "post_id": 1,
        "group": {
            "group_id": 1,
            "name": "Group Name"
        },
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
    ]
    """