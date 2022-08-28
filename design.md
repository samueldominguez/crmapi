# Table of contents <!-- omit in toc -->
- [1. Tech stack choices](#1-tech-stack-choices)
- [2. Data Model](#2-data-model)
  - [2.1. User <a name="dmuser"></a>](#21-user-)
  - [2.2. Customer](#22-customer)
  - [2.3. Role](#23-role)
    - [OAuth2 objects](#oauth2-objects)
- [3. Endpoints](#3-endpoints)
  - [3.1. Authentication](#31-authentication)
    - [3.1.1. POST /api/v1/oauth/token](#311-post-apiv1oauthtoken)
      - [3.1.1.1. **Authentication**](#3111-authentication)
      - [3.1.1.2. **Parameters**](#3112-parameters)
      - [3.1.1.3. **Returns**](#3113-returns)
  - [3.2. User](#32-user)
    - [3.2.1. POST /api/v1/users](#321-post-apiv1users)
      - [3.2.1.1. **Authentication**](#3211-authentication)
      - [3.2.1.2. **Parameters**](#3212-parameters)
      - [3.2.1.3. **Returns**](#3213-returns)
    - [3.2.2. PUT /api/v1/users/<int:id>](#322-put-apiv1usersintid)
      - [3.2.2.1. **Authentication**](#3221-authentication)
      - [3.2.2.2. **Parameters**](#3222-parameters)
      - [3.2.2.3. **Returns**](#3223-returns)
    - [3.2.3. DELETE /api/v1/users/<int:id>](#323-delete-apiv1usersintid)
      - [3.2.3.1. **Authentication**](#3231-authentication)
      - [3.2.3.2. **Parameters**](#3232-parameters)
      - [3.2.3.3. **Returns**](#3233-returns)
    - [3.2.4. GET /api/v1/users/<int:id>](#324-get-apiv1usersintid)
      - [3.2.4.1. **Authentication**](#3241-authentication)
      - [3.2.4.2. **Parameters**](#3242-parameters)
      - [3.2.4.3. **Returns**](#3243-returns)
    - [3.2.5. GET /api/v1/users](#325-get-apiv1users)
      - [3.2.5.1. **Authentication**](#3251-authentication)
      - [3.2.5.2. **Parameters**](#3252-parameters)
      - [3.2.5.3. **Returns**](#3253-returns)
  - [3.3. Customer](#33-customer)
    - [3.3.1. POST /api/v1/customers](#331-post-apiv1customers)
      - [3.3.1.1. **Authentication**](#3311-authentication)
      - [3.3.1.2. **Parameters**](#3312-parameters)
      - [3.3.1.3. **Returns**](#3313-returns)
    - [3.3.2. PUT /api/v1/customers/<int:id>](#332-put-apiv1customersintid)
      - [3.3.2.1. **Authentication**](#3321-authentication)
      - [3.3.2.2. **Parameters**](#3322-parameters)
      - [3.3.2.3. **Returns**](#3323-returns)
    - [3.3.3. DELETE /api/v1/customers/<int:id>](#333-delete-apiv1customersintid)
      - [3.3.3.1. **Authentication**](#3331-authentication)
      - [3.3.3.2. **Parameters**](#3332-parameters)
      - [3.3.3.3. **Returns**](#3333-returns)
    - [3.3.4. GET /api/v1/customers/<int:id>](#334-get-apiv1customersintid)
      - [3.3.4.1. **Authentication**](#3341-authentication)
      - [3.3.4.2. **Parameters**](#3342-parameters)
      - [3.3.4.3. **Returns**](#3343-returns)
    - [3.3.5. GET /api/v1/customers](#335-get-apiv1customers)
      - [3.3.5.1. **Authentication**](#3351-authentication)
      - [3.3.5.2. **Parameters**](#3352-parameters)
      - [3.3.5.3. **Returns**](#3353-returns)
- [4. Other design details](#4-other-design-details)
  - [4.1. OAuth2 tokens](#41-oauth2-tokens)
  - [4.2. Keeping profile pictures "safe"](#42-keeping-profile-pictures-safe)
  - [4.3. Preventing SQL injections and XSS attacks](#43-preventing-sql-injections-and-xss-attacks)
  - [4.4. Pagination on resource lists](#44-pagination-on-resource-lists)

# 1. Tech stack choices
- *Python* - dynamic language with a great library/framework ecosystem for the backend, development speed usually quite fast 
- *Flask* - web microframework, not as many features as Django, but suffices for a REST API
- *Gunicorn* - WSGI production web server, among the most used out there
- *SQLAlchemy* - used as an ORM, lots of documentation, safer and less cumbersome than raw SQL
- *SQLite* - for persistence, due to our usage of an ORM, application code is agnostic to the 'storage engine' behind it. Really easy to set up, and more scalable than it might seem. However, for a production system, something that scale much better like *postgresql* should be used.
- *Docker* - for containerisation, best containerisation tooling out there
- *Pytest* - for unit testing, among the most used unit testing libraries and well documented
- *OAuth2* resource owner password flow. Safer than basic auth on every request, compliant with OAuth2 specs. This type of flow is not the most secure, but the client has the same level of trust as the API beacuse it's developed by the same institution, therefore it's fine to trust the client with the resource owner's credentials

# 2. Data Model
The different objects managed by the API at the user level, not at the implementation level.
## 2.1. User <a name="dmuser"></a>
Represents each user's information. Users can create, read, update and delete customers. Users also can have a variety of roles. Among them, `admin` is the most important. Users with the `admin` role can create, read, update and delete **users**. The following table illustrates the `User` object:
| Property  | Description                | Required                                                  |
| --------- | -------------------------- | --------------------------------------------------------- |
| id        | Primary key                | Automatically generated, required when operating on users |
| user_name | User's user name, unique   | Yes                                                       |
| name      | User's name                | No                                                        |
| surname   | User's surname             | No                                                        |
| roles     | List of the user's `Role`s | No                                                        |

When users are created, a password must be provided. These passwords are hashed via the [key derivation function Argon2](https://en.wikipedia.org/wiki/Argon2), along with a salt that generated at the time of creation, and stored in the database. The user's passwords are not stored in the database in plaintext.

## 2.2. Customer
`Customer` objects represent the customer's information. Customers can be created by any user. The following table illustrates the `Customer` object:
| Property        | Description                                                               | Required                                                      |
| --------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------- |
| id              | Primary key                                                               | Automatically generated, required when operating on customers |
| name            | Customer's name                                                           | Yes                                                           |
| surname         | Customer's surname                                                        | Yes                                                           |
| photoURL        | URL to the customer's profile picture                                     | Yes                                                           |
| last_updated_by | Simple representation of the `User` who last updated this customer object | Automatically generated                                       |
| created_by      | Simple representation of the `User` who created this customer object      | Automatically generated                                       |

`photoURL` field after creation will always point to a picture stored in the API server, which will be served as a static file over HTTP. When creating the customer though, an image file can be passed in the body, or the URL of an image hosted in another server can be passed, where the CRM API will download the picture from said URL and store it in its filesystem. The API will then set that customer's `photoURL` to the file in it's filesystem.

## 2.3. Role
Roles are just a unique string (along with an integer primary key), and their significance is given by the application code. For example, the `admin` role is required by the application to perform any CRUD operation on users.
The following table illustrates the `Role` object:
| Property | Description                                     | Required                                                         |
| -------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| id       | Primary key                                     | Automatically generated, required when dealing with role objects |
| name     | unique string representing the name of the role | Yes                                                              |
### OAuth2 objects
The following are OAauth2 relevant objects:

**OAuth2 Client** represents the client which will connect to the API. The API already comes with a pre-authorised client, and more can be registered manually. The following illustrates the OAuth2 Client object:
| Property  | Description                                | Required                |
| --------- | ------------------------------------------ | ----------------------- |
| id        | Primary key                                | Automatically generated |
| client_id | Identifies each client beyond the database | Yes                     |
| scopes    | Array of scopes allowed to this client     | Yes                     |
| grants    | Array of grants allowed to this client     | Yes                     |

**OAuth2 Grant**
Currently there are two supported grants, `password`, which allows for basic auth, and `refresh_token` which allows for bearer token authentication via a refesh token, provided with the access_token response:
| Property | Description                    | Required                |
| -------- | ------------------------------ | ----------------------- |
| id       | Primary key                    | Automatically generated |
| name     | Identifies each grant uniquely | Yes                     |

**OAuth2 Scope**
This is actually just `Role`, there is no Oauth2 scope object.

# 3. Endpoints
## 3.1. Authentication
### 3.1.1. POST /api/v1/oauth/token
#### 3.1.1.1. **Authentication**
Basic auth with `user_name` and `password` specified during user creation, or via bearer token with the `refresh_token` generated along with the `access_token`
#### 3.1.1.2. **Parameters**
- `client_id` identifies the client using the API, a client has already been generated for testing purposes, check [config_dev.py](config_dev.py)
- `grant` this should be `password` if obtaining the access_token for the first time and using basic auth, or `refresh_token` if using the refresh token to obtain a new access_token
- `scope` the scopes the client wants to have access to (ultimately, the scopes the users using this particular client will have access to, even if the users have access to these scopes, if the client is not authorised to use these scopes, the users won't be able to use them). `scope` here is just OAuth2 semantics for the `Role` object defined in [app/models.py](app/models.py). Please **note** that if you are refreshing your access token via a refresh token, you do not need to specify the scopes as those are encoded in the JWT token
#### 3.1.1.3. **Returns**
- `access_token` bearer token to use in all other endpoints
- `issued_at` unix timestamp indicating when the token was generated
- `expires_in` the amount of seconds from `issued_at` the token will be valid for
- `token_type` the token type, always `BearerToken` in our case
- `scope` the subset of requested scopes the API allows the client to use with this token
- `grant` the type of grant requested, reflected back to the user
- `client_id` the ID of the client that made the request, reflected back to the user
- `refresh_token` the bearer token used to obtain a new `access_token` (and refresh token)
- `refresh_token_expires_in` amount of seconds from `issued_at` the refresh token will be valid for

e.g.:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NjE3MjQyNTYsInVzZXJfaWQiOjEsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.VBUA3KRhKwG4dhik7SnRNOkHEzZ3XqaNvI96HuD8V6M",
    "issued_at": 1661720656,
    "expires_in": 3600,
    "token_type": "BearerToken",
    "scope": "admin,wizard",
    "grant": "password",
    "client_id": "AEwgqY-ZTyBwPUtllgoDoKyElMV6PuFdflA14FG6Br6gY4ag4TwYcnjy8A02dQJp9L7n8z8YhLc0BgATKVNaRg",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NjE3Mjc4NTYsInVzZXJfaWQiOjEsInNjb3BlIjoiYWRtaW4sd2l6YXJkIiwidHlwZSI6InJlZnJlc2hfdG9rZW4ifQ.1rPfgmzUBWHkOr_34_tqUbg8VW5pcwKY_3V-B66-meg",
    "refresh_token_expires_in": 7200
}
```
## 3.2. User
**NOTE**: all user endpoints are authorized only to users with the `admin` role.
### 3.2.1. POST /api/v1/users
Create users
#### 3.2.1.1. **Authentication**
Bearer token authentication
#### 3.2.1.2. **Parameters**
- `user_name` user's user name
- `password` the user's login password for basic auth
- `name` user's name
- `surname` user's surname
- `roles` comma separated list of roles, they must exist
#### 3.2.1.3. **Returns**
On success returns the user just created, status code 201
### 3.2.2. PUT /api/v1/users/<int:id>
Updates the a user by id
#### 3.2.2.1. **Authentication**
Bearer token authentication
#### 3.2.2.2. **Parameters**
- `user_name` user's user name
- `password` the user's login password for basic auth
- `name` user's name
- `surname` user's surname
- `roles` comma separated list of roles, they must exist
#### 3.2.2.3. **Returns**
On success returns the user just updated, status code 200
### 3.2.3. DELETE /api/v1/users/<int:id>
Deletes a user by id
#### 3.2.3.1. **Authentication**
Bearer token authentication
#### 3.2.3.2. **Parameters**
None.
#### 3.2.3.3. **Returns**
On sucess returns no body with status code 204
### 3.2.4. GET /api/v1/users/<int:id>
Returns a user object by id
#### 3.2.4.1. **Authentication**
Bearer token authentication
#### 3.2.4.2. **Parameters**
None
#### 3.2.4.3. **Returns**
On sucess returns the user object with the specified id, status code 200
### 3.2.5. GET /api/v1/users
Return a list of all users, paginated
#### 3.2.5.1. **Authentication**
Bearer token authentication
#### 3.2.5.2. **Parameters**
- `page` which page of results, defaults to 1
- `per_page` how many results per page, defaults to 100
#### 3.2.5.3. **Returns**
An array of user objects corresponding to the established pagination. The `Link` header in the response contains two URLs, one for the next page, and one for the last page. The `X-Total-Count` header specifies the current total number of users. See the [pagination section for more details.](#pagination-on-resource-lists) 
## 3.3. Customer
### 3.3.1. POST /api/v1/customers
Create a customer record
#### 3.3.1.1. **Authentication**
Bearer token authentication
#### 3.3.1.2. **Parameters**
- `name` customer's name
- `surname` customer's surname
- `photoURL` URL to a photo to be used as profile picture, the API will try to download this
- `file` **in body's form data** with a picture, allowed formats: `png`, `jpg`, `jpeg`

The API will download the picture in `photoURL` and save it in it's filesystem with a random file name. If `photoURL` is not present, it will check the request's form-data in the body, and look for the `file` key. It will save it to it's filesystem and again generate a random file name.
#### 3.3.1.3. **Returns**
Returns the customer object just created. The `photoURL` field will be a URL somewhere in the API server where the profile picture is hosted. The customer object keeps track of the user who created it, and will return this in the response.
### 3.3.2. PUT /api/v1/customers/<int:id>
Update a customer record
#### 3.3.2.1. **Authentication**
Bearer token authentication
#### 3.3.2.2. **Parameters**
- `name` customer's name
- `surname` customer's surname
- `photoURL` URL to a photo to be used as profile picture, the API will try to download this
- `file` **in body's form data** with a picture, allowed formats: `png`, `jpg`, `jpeg`

The API will download the picture in `photoURL` and save it in it's filesystem with a random file name. If `photoURL` is not present, it will check the request's form-data in the body, and look for the `file` key. It will save it to it's filesystem and again generate a random file name.
#### 3.3.2.3. **Returns**
Returns the customer object just updated. The customer object also keeps track of the user who last updated it, and will return this in the response as well.
### 3.3.3. DELETE /api/v1/customers/<int:id>
Deletes a customer by id
#### 3.3.3.1. **Authentication**
Bearer token authentication
#### 3.3.3.2. **Parameters**
None.
#### 3.3.3.3. **Returns**
When successful returns no body, status code 204
### 3.3.4. GET /api/v1/customers/<int:id>
Return a customer by id
#### 3.3.4.1. **Authentication**
Bearer token authentication
#### 3.3.4.2. **Parameters**
None.
#### 3.3.4.3. **Returns**
When successful returns a customer record, status code 200
### 3.3.5. GET /api/v1/customers
Return a list of all customers, paginated
#### 3.3.5.1. **Authentication**
Bearer token authentication
#### 3.3.5.2. **Parameters**
- `page` which page of results, defaults to 1
- `per_page` how many results per page, defaults to 100
#### 3.3.5.3. **Returns**
An array of customer objects corresponding to the established pagination. The `Link` header in the response contains two URLs, one for the next page, and one for the last page. The `X-Total-Count` header specifies the current total number of users. See the [pagination section for more details.](#pagination-on-resource-lists) 
# 4. Other design details
## 4.1. OAuth2 tokens
The access token and refresh_token received after a password grant, or via a refresh_token grant is a JWT. The payload of this token contains:
1. expiry time
2. user ID
3. type (either `access_token` or `refresh_token`)
4. scope (to continue generating new tokens with the originally requested set of scopes)

By keeping this data in the token itself, after successful decoding, we can verify the user exists and their role by performing a database lookup, to check whether the endpoint is authorised for them, effectively acting as a kind of session. The user role could be embedded in the JWT, however this means any role updates between token generation and its expiry would not take effect, unless the database was queried to verify it, which would defeat the point of encoding it in the token. Expiry time however, will not change, and therefore can be put in the token itself, which saves having to store it and an additional JOIN.

The type allows us check whether a refresh token is being sent when authorising a non oauth endpoint, since refresh tokens are also sent as bearer tokens. Refresh tokens are only used to generate a new set of tokens. By decoding the payload and checking the type we can avoid this.

By keeping the scope of the token in the token itself, we can make sure it only authorises the originally requested set of scopes. The refresh token will also generate new tokens with the same original set of scopes.
## 4.2. Keeping profile pictures "safe"
Profile pictures are not protected behind any authentication or authorization. They are served when requested by anybody. However, the file names of uploaded images are always replaced by a random 64 byte string, which in effect makes it a sort of password. The only privacy concern would come from a user sharing the URL of any of these pictures. Once someone is in posession of an image URL, they will always have access to them, but this shouldn't be a major privacy concern.
## 4.3. Preventing SQL injections and XSS attacks
By only accessing storage via the ORM, we are virtually invulnerable to *SQL injection* attacks. XSS attacks have been mitigated though the following measures:
1. All responses with content, are of `application/json` types or images. This means any malicious javascript reflected in the response should not be interpreted as such, except with a few exceptions, which are hopefully mitigated by the next measure
2. `X-Content-Type-Options` set to `nosniff` so browsers do not try to 'sniff' the content type and stick to the `Content-Type` header
3. All `text/html` and `application/json` responses have been cleansed of potentially malicious tags via the [python bleach package](https://pypi.org/project/bleach/). It's probably overkill to *bleach* json responses, but one can never be too careful.

## 4.4. Pagination on resource lists
Pagination has been implemented loosely based on [this article](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#pagination).

For `GET`s on a resource without specifying an `id`, we return a list of those resources, limited by default to `100` results per call. Subsequent sets of results can be obtained via the `page` parameter, starting at 1. However, the size of each page can also be specified via `per_page`. For example:
- `GET /api/v1/customers` returns first 100 results of the first page
- `GET /api/v1/customers?page=33&per_page=25` returns page number 33 where each page has 25 (or less if we are on the last page and the total isn't a multiple of the page size) results

For convenience and according to the [RFC288](https://www.rfc-editor.org/rfc/rfc8288), the `Link` header contains a link to the next page and to the last page. If the next and last pages are the same URL, then that means you've reached the last page.

Additionally, and beyond current standards as of teh writing of this design document, the header `X-Total-Count` is also added to each response, containing the total number of elements for the resource being accessed.