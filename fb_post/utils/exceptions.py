from django.core.exceptions import *



class InvalidUserException(Exception):
     pass

class InvalidGroupNameException(Exception):
    pass

class InvalidMemberException(Exception):
    pass

class InvalidPostContent(Exception):
    pass

class InvalidGroupException(Exception):
    pass

class UserIsNotAdminException(Exception):
    pass

class UserNotInGroupException(Exception):
    pass

class InvalidPostException(Exception):
    pass

class InvalidCommentException(Exception):
    pass

class InvalidCommentContent(Exception):
    pass

class InvalidReplyContent(Exception):
    pass

class InvalidReactionTypeException(Exception):
    pass

class UserCannotDeletePostException(PermissionDenied):
    pass