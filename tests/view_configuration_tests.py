from django.test.client import RequestFactory
from mock import ANY, Mock, patch
from unittest2 import TestCase

from test_views import TestProxy


class RequestPatchMixin(object):
    def patch_request(self, mock_response=None):
        """patches requests.request and sets its return_value"""
        self.request_patcher = patch('djproxy.views.request')
        self.request = self.request_patcher.start()

        self.request.return_value = mock_response

        self.mock_response = mock_response

        return self.request


class HttpProxyConfigVerification(TestCase, RequestPatchMixin):
    def setUp(self):
        self.fake_request = RequestFactory().get('/')
        self.proxy = TestProxy.as_view()

        self.orig_base_url = TestProxy.base_url
        self.orig_downstream_headers = TestProxy.ignored_downstream_headers
        self.orig_request_headers = TestProxy.ignored_request_headers

        # Keep things fast by making sure that proxying doesn't actually
        # happen in these tests:
        self.patch_request(Mock(raw='', status_code=200, headers={}))

    def tearDown(self):
        TestProxy.base_url = self.orig_base_url
        TestProxy.ignored_downstream_headers = self.orig_downstream_headers
        TestProxy.ignored_request_headers = self.orig_request_headers

    def test_raises_an_exception_if_the_proxy_has_no_base_url(self):
        TestProxy.base_url = ''
        self.assertRaises(AssertionError, self.proxy, self.fake_request)

    def test_raises_an_exception_if_downstream_ignore_list_not_iterable(self):
        TestProxy.ignored_downstream_headers = None
        self.assertRaises(TypeError, self.proxy, self.fake_request)

    def test_raises_an_exception_if_request_headers_ignore_list_not_iterable(
            self):
        TestProxy.ignored_request_headers = None
        self.assertRaises(TypeError, self.proxy, self.fake_request)

    def test_passes_if_the_base_url_is_set(self):
        self.proxy(self.fake_request)


class HttpProxyUrlConstructionWithoutURLKwarg(TestCase, RequestPatchMixin):
    """HttpProxy proxy url construction without a URL kwarg"""
    def setUp(self):
        self.fake_request = RequestFactory().get('/yay/')
        self.proxy = TestProxy.as_view()

        self.patch_request(Mock(raw='', status_code=200, headers={}))

        self.proxy(self.fake_request)

    def test_only_contains_base_url_if_no_default_url_configured(self):
        """only contains base_url"""
        self.request.assert_called_once_with(
            method=ANY, url="https://google.com/", data=ANY, headers=ANY,
            files=ANY, params=ANY)


class HttpProxyUrlConstructionWithURLKwarg(TestCase, RequestPatchMixin):
    """HttpProxy proxy url construction with a URL kwarg"""
    def setUp(self):
        self.fake_request = RequestFactory().get('/yay/')
        self.proxy = TestProxy.as_view()

        self.patch_request(Mock(raw='', status_code=200, headers={}))

        self.proxy(self.fake_request, url="yay/")

    def test_urljoins_base_url_and_url_kwarg(self):
        """urljoins base_url and url kwarg"""
        self.request.assert_called_once_with(
            method=ANY, url="https://google.com/yay/", data=ANY, headers=ANY,
            files=ANY, params=ANY)