from headers import HeaderDict


class DownstreamRequest(object):

    """A Django request wrapper that provides utilities for proxies.

    Attributes that do not exist on this class are deferred to the Django
    request object used to create the instance.

    """

    def __init__(self, request):
        self._request = request

    @property
    def headers(self):
        """Request headers."""
        request_headers = HeaderDict()
        other_headers = ['CONTENT_TYPE', 'CONTENT_LENGTH']

        for header, value in self._request.META.iteritems():
            is_header = header.startswith('HTTP_') or header in other_headers
            normalized_header = self._normalize_django_header_name(header)

            if is_header and value:
                request_headers[normalized_header] = value

        return request_headers

    @property
    def query_string(self):
        """Request query string."""
        return self._request.META['QUERY_STRING']

    @property
    def x_forwarded_for(self):
        """X-Forwarded-For header value.

        This is the amended header so that it contains the previous IP address
        in the forwarding change.

        """
        ip = self._request.META.get('REMOTE_ADDR')
        current_xff = self.headers.get('X-Forwarded-For')

        return '%s, %s' % (current_xff, ip) if current_xff else ip

    def _normalize_django_header_name(self, header):
        """Unmunge header names modified by Django."""
        # Remove HTTP_ prefix.
        new_header = header.rpartition('HTTP_')[2]
        # Camel case and replace _ with -
        new_header = '-'.join(
            x.capitalize() for x in new_header.split('_'))

        return new_header

    def __getattr__(self, name):
        return getattr(self._request, name)
