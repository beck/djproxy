class HeaderDict(dict):

    """A dict containing header, value pairings."""

    def filter(self, exclude):
        """Return a HeaderSet excluding the headers in the exclude list."""
        filtered_headers = HeaderDict()
        lowercased_ignore_list = map(lambda x: x.lower(), exclude)

        for header, value in self.iteritems():
            if header.lower() not in lowercased_ignore_list:
                filtered_headers[header] = value

        return filtered_headers
