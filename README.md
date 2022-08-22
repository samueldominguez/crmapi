# Notes to self
- can probably leverage `marshmallow` for serializing SQLAlchemy models, idk if it automatically sanitizes inputs to prevent XSS
- Image uploads will have have e random string as their filename to increase privacy
- Dockerize and TDD ASAP
- Investigate CD tooling
- I could go for OAuth2 but current scheme works well
- Could create a roles object and add various roles to each user, `admin` among them, then have the decorator check for a specific role for the user in question