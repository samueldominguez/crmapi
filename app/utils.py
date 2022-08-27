from flask import url_for, current_app, jsonify


def bad_req_handler(error):
    """Return the error string as json with status 400"""
    return jsonify({'error': error}), 400


def gen_link_header(url_next, url_last):
    """Format pagination's next and last urls for Link header"""
    return '<{}>; rel="next", <{}>; rel="last"'.format(url_next, url_last)


def fill_response_with_pagination_headers(resp, page, per_page, total, route_name, args):
    """
    Get Reponse object and fill it with pagination headers:
    Link: has URLs for next page and last page
    X-Total-Count: total elements of the given resource
    """
    args = dict(args)
    last_page = (total // per_page) + (1 if total % per_page != 0 else 0)
    next_page = page + 1 if page != last_page else page
    args['per_page'] = per_page
    args['page'] = next_page
    url_next = url_for(route_name, _external=True, **args)
    args['page'] = last_page
    url_last = url_for(route_name, _external=True, **args)
    resp.headers['Link'] = gen_link_header(url_next, url_last)
    resp.headers['X-Total-Count'] = str(total)
    return resp


def allowed_file(filename):
    """Check if file name is valid for upload into server"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower(
        ) in current_app.config.get('ALLOWED_EXTENSIONS')
