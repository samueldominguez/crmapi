# Table of contents
- [Table of contents](#table-of-contents)
- [Tech stack choices](#tech-stack-choices)
- [Data Model](#data-model)
  - [User <a name="dmuser"></a>](#user-)
  - [Customer](#customer)
  - [Role](#role)
- [Endpoints](#endpoints)
  - [Authentication](#authentication)
    - [POST /api/v1/tokens](#post-apiv1tokens)
      - [**Authentication**](#authentication-1)
      - [**Parameters**](#parameters)
      - [**Returns**](#returns)
  - [User <a name="epuser"></a>](#user--1)
    - [POST /api/v1/users](#post-apiv1users)
  - [Customer <a name="epcustomer"></a>](#customer-)
    - [POST /api/v1/customers](#post-apiv1customers)
- [Other design details](#other-design-details)
  - [Token format](#token-format)
  - [Keeping profile pictures "safe"](#keeping-profile-pictures-safe)
  - [Preventing SQL injections and XSS attacks](#preventing-sql-injections-and-xss-attacks)
  - [Pagination on resource lists](#pagination-on-resource-lists)

# Tech stack choices
- *Python* - great library/framework ecosystem for the backend, development speed usually quite fast 
- *Flask* - web microframework, not as many features as Django, but suffices for a REST API
- *Gunicorn* - WSGI production web server, among the most stable WSGIs out there
- *SQLAlchemy* - used for an ORM, lots of documentation, more safe and less cumbersome than patching aplication code with SQL queries
- *SQLite* - for persistence, due to our usage of an ORM, application code is agnostic to the 'storage engine' behind it. Really easy to set up, and more scalable than it might seem. However, for a production system, something that scale much better like *postgresql* should be used.
- *Docker* - for containerisation, best containerisation tooling out there
- *Pytest* - for unit testing, among the most used unit testing libraries and well documented
- Basic Auth into Bearer Auth (similar to and simpler than OAuth2) - safer than basic auth on every request, but not compliant to OAuth2 standard, this is definitely on the TODO list.

# Data Model
The different objects managed by the API at the user level, not at the implementation level.
## User <a name="dmuser"></a>
Represents each user's information. Users can create, read, update and delete customers. Users also can have a variety of roles. Among them, `admin` is the most important. Users with the `admin` role can create, read, update and delete **users**. The following table illustrates the `User` object:
| Property  | Description                | Required                                                  |
| --------- | -------------------------- | --------------------------------------------------------- |
| id        | Primary key                | Automatically generated, required when operating on users |
| user_name | User's user name, unique   | Yes                                                       |
| name      | User's name                | No                                                        |
| surname   | User's surname             | No                                                        |
| roles     | List of the user's `Role`s | No                                                        |

When users are created, a password must be provided. These passwords are hashed via the [key derivation function Argon2](https://en.wikipedia.org/wiki/Argon2), along with a salt that generated at the time of creation, and stored in the database. The user's passwords are not stored in the database in plaintext.

## Customer
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

## Role
Roles are just a unique string (along with an integer primary key), and their significance is given by the application code. For example, the `admin` role is required by the application to perform any CRUD operation on users.
The following table illustrates the `Role` object:
| Property | Description                                     | Required                                                         |
| -------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| id       | Primary key                                     | Automatically generated, required when dealing with role objects |
| name     | unique string representing the name of the role | Yes                                                              |

# Endpoints
## Authentication
### POST /api/v1/tokens
#### **Authentication**
Basic auth with `user_name` and `password` specified during user creation
#### **Parameters**
None.
#### **Returns**
- `expires_at` datetime in UTC, iso format, specifies when token expires
- `token` the token to use for authentication in all other endpoints

e.g.:
```json
{
    "expires_at": "2022-08-25T16:18:44.228848+00:00",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NjE0MjMzNzcsInVzZXJfaWQiOjJ9.xi_9gYELYE8SgO4qvS_IKZEPB4K1LtYf5Y-i0J8oQ8M"
}
```
## User <a name="epuser"></a>
### POST /api/v1/users
blah
## Customer <a name="epcustomer"></a>
### POST /api/v1/customers
blah
# Other design details
## Token format
The token received after a successful basic auth is a JWT. The payload of this token contains:
1. expiry time
2. user ID

By keeping this data in the token itself, after successful decoding, we can verify the user exists and their role by performing a database lookup, to check whether the endpoint is authorised for them, effectively acting as a kind of session. The user role could be embedded in the JWT, however this means any role updates between token generation and its expiry would not take effect, unless the database was queried to verify it, which would defeat the point of encoding it in the token. Expiry time however, will not change, and therefore can be put in the token itself, which saves having to store it and an additional JOIN.
## Keeping profile pictures "safe"
Profile pictures are not protected behind any authentication or authorization. They are served when requested by anybody. However, the file names of uploaded images are always replaced by a random 64 byte string, which in effect makes it a sort of password. The only privacy concern would come from a user sharing the URL of any of these pictures. Once someone is in posession of an image URL, they will always have access to them, but this shouldn't be a major privacy concern.
## Preventing SQL injections and XSS attacks
By only accessing storage via the ORM, we are virtually invulnerable to *SQL injection* attacks. XSS attacks have been mitigated though the following measures:
1. All responses with content, are of `application/json` types or images. This means any malicious javascript reflected in the response should not be interpreted as such, except with a few exceptions, which are hopefully mitigated by the next measure
2. `X-Content-Type-Options` set to `nosniff` so browsers do not try to 'sniff' the content type and stick to the `Content-Type` header
3. All `text/html` and `application/json` responses have been cleansed of potentially malicious tags via the [python bleach package](https://pypi.org/project/bleach/). It's probably overkill to *bleach* json responses, but one can never be too careful.

## Pagination on resource lists
Pagination has been implemented loosely based on [this article](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#pagination).

For `GET`s on a resource without specifying an `id`, we return a list of those resources, limited by default to `100` results per call. Subsequent sets of results can be obtained via the `page` parameter, starting at 1. However, the size of each page can also be specified via `per_page`. For example:
- `GET /api/v1/customers` returns first 100 results of the first page
- `GET /api/v1/customers?page=33&per_page=25` returns page number 33 where each page has 25 (or less if we are on the last page and the total isn't a multiple of the page size) results

For convenience and according to the [RFC288](https://www.rfc-editor.org/rfc/rfc8288), the `Link` header contains a link to the next page and to the last page. If the next and last pages are the same URL, then that means you've reached the last page.

Additionally, and beyond current standards as of teh writing of this design document, the header `X-Total-Count` is also added to each response, containing the total number of elements for the resource being accessed.