# Facebook Clone Backend (Django + GraphQL)

A minimal Facebook-like backend built with Django and Graphene (GraphQL). It models users, groups, posts, comments (with nested replies), and reactions, and exposes read-only GraphQL queries with an in-browser GraphiQL IDE.

## Tech Stack

- **Python**: 3.10+ recommended
- **Django**: 5.2.x (project scaffold comment mentions 4.1; runtime uses 5.2.x per `requirements.txt`)
- **GraphQL**: Graphene (`graphene`, `graphene-django`)
- **Database**: SQLite (default)

See `requirements.txt` for exact versions.

## Project Structure

- `facebook_clone_backend/`
  - `settings.py`: Django settings — `INSTALLED_APPS` includes `fb_post` and `graphene_django`; timezone `Asia/Kolkata`; SQLite DB.
  - `urls.py`: Routes admin and includes `fb_post.urls` (GraphQL).
- `fb_post/`
  - `models.py`: Core data models.
  - `schema.py`: GraphQL types and queries.
  - `urls.py`: Exposes `/graphql` with GraphiQL enabled.
  - `constants/enum.py`: `ReactionType` enum values.
- `templates/`: Template dir is configured but optional here.
- `db.sqlite3`: Local dev database.
- `manage.py`: Django management entrypoint.

## Data Model Overview

Defined in `fb_post/models.py`:

- **User**
  - `user_id` (PK, AutoField)
  - `name` (CharField)
  - `profile_pic` (TextField)

- **Group**
  - `name` (CharField)
  - `members` Many-to-Many to `User` via `Membership`

- **Membership** (through table for `Group.members`)
  - `group` (FK -> Group)
  - `member` (FK -> User, `related_name='user_membership'`)
  - `is_admin` (Boolean)

- **Post**
  - `post_id` (PK, AutoField)
  - `content` (CharField)
  - `posted_at` (DateTimeField)
  - `posted_by` (FK -> User)
  - `group` (FK -> Group)
  - `Meta.ordering = ['-post_id']`

- **Comment**
  - `comment_id` (PK, AutoField)
  - `content` (CharField)
  - `commented_at` (DateTimeField)
  - `commented_by` (FK -> User, nullable)
  - `post` (FK -> Post, `related_name='commenter'`, nullable)
  - `reply` (FK -> Comment self, `related_name='reply_to_comment'`, nullable)

- **React**
  - `reaction` (CharField with choices from `ReactionType`)
  - `post` (FK -> Post, nullable)
  - `comment` (FK -> Comment, nullable)
  - `reacted_at` (DateTimeField)
  - `reacted_by` (FK -> User)

Reaction types in `fb_post/constants/enum.py`:
- `WOW`, `LIT`, `LOVE`, `HAHA`, `THUMBS - UP`, `THUMBS - DOWN`, `ANGRY`, `SAD`

## GraphQL API

- **Endpoint**: `/<root>/graphql`
  - Wired in `fb_post/urls.py`
  - GraphiQL enabled: `GraphQLView.as_view(graphiql=True, schema=schema)`
- **Schema**: `fb_post/schema.py`
  - Types: `UserType`, `GroupType`, `PostType`, `CommentType`, `ReactType`
  - Relations resolved via database queries.

### Available Queries

- `all_users: [UserType]`
- `user(user_id: Int!): UserType`
- `all_posts: [PostType]`
- `all_comments: [CommentType]`
- `all_reacts: [ReactType]`
- `all_groups: [GroupType]`
- `all_posts_by_user(user_id: Int!): [PostType]`
- `all_comments_by_post(post_id: Int!): [CommentType]`
- `all_reacts_by_post(post_id: Int!): [ReactType]`
- `posts_by_user_with_comments_and_reactions(user_id: Int!): [PostType]`

Note: This project currently exposes read-only queries; no mutations are defined.

### Sample Queries

Fetch posts with comments and reactions for a user:

```graphql
query PostsByUser($uid: Int!) {
  posts_by_user_with_comments_and_reactions(user_id: $uid) {
    post_id
    content
    posted_at
    posted_by { user_id name }
    group { id name }
    comments {
      comment_id
      content
      commented_at
      commented_by { user_id name }
      replies { comment_id content }
      reactions { reaction reacted_at reacted_by { user_id name } }
    }
    reactions { reaction reacted_at reacted_by { user_id name } }
  }
}
```

List all users:

```graphql
query { all_users { user_id name profile_pic } }
```

Get a single user:

```graphql
query { user(user_id: 1) { user_id name profile_pic } }
```

Comments by post:

```graphql
query { all_comments_by_post(post_id: 1) { comment_id content commented_by { name } } }
```

## Getting Started

1) **Clone & create a virtualenv**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows PowerShell
```

2) **Install dependencies**

```bash
pip install -r requirements.txt
```

3) **Apply migrations**

```bash
python manage.py migrate
```

4) **Run the server**

```bash
python manage.py runserver
```

5) **Open GraphiQL**

- Navigate to `http://127.0.0.1:8000/graphql` and run queries.

## Configuration Notes

- `TIME_ZONE`: `Asia/Kolkata` in `facebook_clone_backend/settings.py`.
- `USE_TZ = False`.
- Database: SQLite (`db.sqlite3`).
- Static base URL: `/static/`.
- Templates dir: `BASE_DIR/templates`.

## Admin (optional)

Django admin is enabled at `/admin`. Create a superuser to sign in:

```bash
python manage.py createsuperuser
```

## Testing

Basic test scaffold exists under `fb_post/tests/`. Add unit tests for models and resolvers as needed.

## License

No explicit license provided. Consider adding one if you plan to share publicly.
