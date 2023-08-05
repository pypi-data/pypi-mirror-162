import re

try:
    from json.decoder import JSONDecodeError
except ImportError:
    # For python2.7
    JSONDecodeError = ValueError

from .errors import AuthenticationError, NotFoundError, ServerError


def get_err_msg(res):
    '''
    Utility function to paper over different ways an error message may be
    returned.
    '''
    err = None
    try:
        # attempt to parse response as JSON, first
        json = res.json()

        # attempt `error.message`
        err = json['error'].get('message') if 'error' in json else None

        # attempt to append extra details
        if err:
            details = json["error"].get("details")
            if isinstance(details, list):
                err += ': '
                for detail in details:
                    msg = detail.get("message", detail)
                    err += '{}; '.format(msg)
                err = err[:-2]  # strip final `; `

        # attempt `message` or `error` (not nested)
        if not err:
            err = json.get('message', json.get('error'))

        # give up
        if not err:
            err = str(json)
    except JSONDecodeError as ex:
        err = 'Invalid JSON returned by server: {}'.format(ex)

    return err


def parse_or_raise(res, dont_parse=False, raise_for_404=True):
    '''
    Validates the status code of `res`, and automatically raises specific
    exceptions if necessary. Otherwise, returns the `.json()` of the response.

    :param req: Response object to validate.
    :type req: requests.Response

    :param dont_parse: Whether to not call `.json()` on the `res` object.
    :type dont_parse: bool, optional

    :param raise_for_404: Whether to raise on 404 responses.
    :type raise_for_404: bool, optional

    :raises AuthenticationError: Upon HTTP 401.
    :raises NotFoundError: Upon HTTP 404.
    :raises ValueError: Upon HTTP 4XX (except the ones specifically listed).
    :raises ServerError: Upon HTTP 500.
    '''
    if res.status_code == 401:
        raise AuthenticationError()

    if res.status_code == 404:
        if raise_for_404:
            raise NotFoundError(get_err_msg(res))

        return None

    # some routes throw other codes than the ones listed... catch everything
    # 400~500 just for peace of mind
    if res.status_code >= 400 and res.status_code < 500:
        raise ValueError(get_err_msg(res))

    if res.status_code >= 500:
        raise ServerError(get_err_msg(res))

    return res if dont_parse else res.json()


def rewrite_docstring_for_external_client(docstring):
    '''
    Rewrites the docstring for a method from `Client` (which usually receives a
    DocumentType param) to use within `ExternalClient` (which receives a
    ExternalDocumentType param).

    :param docstring: Original docstring.
    :type docstring: str

    :return: Updated docstring.
    :rtype: str
    '''
    return re.sub(r'\bDocumentType\b', 'ExternalDocumentType', docstring)
