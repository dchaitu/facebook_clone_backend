from django.db import models
from fb_post.constants.enum import ReactionType


# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    profile_pic = models.TextField()

    def __str__(self):
        return self.name

    def get_user_dict(self):
        return {"user_id":self.user_id,"name":self.name,"profile_pic":self.profile_pic}


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, through='Membership')

    def __str__(self):
        return f'{self.name}'

    def get_group_dict(self):
        return {"group_id":self.id,"name":self.name}

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_membership')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f'Membership for {self.group.name}'



class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=1000)
    posted_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return "{} Posted {}".format(self.posted_by.name, self.content)

    def get_post_dict(self):
        return {"post_id":self.post_id,"group":self.group.get_group_dict(), "posted_by":self.posted_by.get_user_dict(), "posted_at":self.posted_at.strftime("%Y-%m-%d %H:%M:%S"), "post_content":self.content}

    class Meta:
        ordering = ['-post_id']

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=1000)
    commented_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, related_name="commenter", on_delete=models.CASCADE, blank=True, null=True)
    reply = models.ForeignKey('self', related_name="reply_to_comment", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.reply:
            return "{} replied {}".format(self.commented_by.name, self.content)
        else:
            return "{} commented on {}".format(self.commented_by.name, self.post.content)

    def get_comment_dict(self):
        return {"comment_id":self.comment_id,"commenter":self.commented_by.get_user_dict(),"commented_at":self.commented_at.strftime("%Y-%m-%d %H:%M:%S"),"comment_content":self.content}

class React(models.Model):
    reaction = models.CharField(choices=[(tag.value,tag) for tag in ReactionType], max_length=100)
    post = models.ForeignKey(Post, related_name="reacted_to_post", on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, related_name="commented_to_the_post", on_delete=models.CASCADE, blank=True,
                                null=True)
    reacted_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    reacted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Feeling {} by {}".format(self.reaction, self.reacted_by.name)
