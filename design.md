# Tech stack
- Python
- Flask as the web framework
- Gunicorn as the prod web server
- SQLAlchemy for the ORM
- Postgres for storage
- Docker for containerisation
- Pytest for unit testing
- OAuth 2 for authentication (this is a nice but not a must)

## Pagination
Pagination has been implemented loosely based on [this article](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#pagination).

For `GET`s on a resource without specifying an `id`, we return a list of those resources, limited by default to `100` results per call. Subsequent sets of results can be obtained via the `page` parameter, starting at 1. However, the size of each page can also be specified via `per_page`. For example:
- `GET /api/v1/customers` returns first 100 results of the first page
- `GET /api/v1/customers?page=33&per_page=25` returns page number 33 where each page has 25 (or less if we are on the last page and the total isn't a multiple of the page size) results

For convenience and according to the [RFC288](https://www.rfc-editor.org/rfc/rfc8288), the `Link` header contains a link to the next page and to the last page. If the next and last pages are the same URL, then that means you've reached the last page.

Additionally, and beyond current standards as of teh writing of this design document, the header `X-Total-Count` is also added to each response, containing the total number of elements for the resource being accessed.