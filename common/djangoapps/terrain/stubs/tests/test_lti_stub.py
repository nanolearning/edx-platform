"""
Unit tests for stub LTI implementation.
"""
import mock
from mock import Mock
import unittest
import threading
import textwrap
import urllib
import requests
from terrain.stubs.lti import StubLtiService


class StubLtiServiceTest(unittest.TestCase):
    """
    A stub of the LTI provider that listens on a local
    port and responds with pre-defined grade messages.

    Used for lettuce BDD tests in lms/courseware/features/lti.feature
    """

    def setUp(self):
        self.server = StubLtiService()

        lti_base = self.server.config('lti_base', self.server.DEFAULT_LTI_BASE)
        lti_endpoint = self.server.config('lti_endpoint', self.server.DEFAULT_LTI_ENDPOINT)
        self.uri = lti_base + lti_endpoint

         # Flag for creating right callback_url
        self.server.set_config('test_mode', True)
        self.server.set_config('run_inside_unittest_flag', True)
        self.addCleanup(self.server.shutdown)

    def test_wrong_header(self):
        """
        Tests that LTI server processes request with right program path but with wrong header.
        """
        #wrong number of params and no signature
        payload = {
            'user_id': 'default_user_id',
            'role': 'student',
            'oauth_nonce': '',
            'oauth_timestamp': '',
        }
        headers = {'referer': 'http://localhost:8000/'}
        response = requests.post(self.uri, data=payload, headers=headers)
        self.assertIn('Wrong LTI signature', response.content)

    def test_wrong_signature(self):
        """
        Tests that LTI server processes request with right program
        path and responses with incorrect signature.
        """
        payload = {
            'user_id': 'default_user_id',
            'role': 'student',
            'oauth_nonce': '',
            'oauth_timestamp': '',
            'oauth_consumer_key': 'test_client_key',
            'lti_version': 'LTI-1p0',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0',
            'oauth_signature': '',
            'lti_message_type': 'basic-lti-launch-request',
            'oauth_callback': 'about:blank',
            'launch_presentation_return_url': '',
            'lis_outcome_service_url': '',
            'lis_result_sourcedid': '',
            'resource_link_id':'',
        }
        headers = {'referer': 'http://localhost:8000/'}
        response = requests.post(self.uri, data=payload, headers=headers)
        self.assertIn('Wrong LTI signature', response.content)


    def test_success_response_launch_lti(self):
        """
        Success lti launch.
        """
        payload = {
            'user_id': 'default_user_id',
            'role': 'student',
            'oauth_nonce': '',
            'oauth_timestamp': '',
            'oauth_consumer_key': 'test_client_key',
            'lti_version': 'LTI-1p0',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0',
            'oauth_signature': '',
            'lti_message_type': 'basic-lti-launch-request',
            'oauth_callback': 'about:blank',
            'launch_presentation_return_url': '',
            'lis_outcome_service_url': '',
            'lis_result_sourcedid': '',
            'resource_link_id':'',
        }
        self.server.check_oauth_signature = Mock(return_value=True)
        headers = {'referer': 'http://localhost:8000/'}
        response = requests.post(self.uri, data=payload, headers=headers)
        self.assertIn('This is LTI tool. Success.', response.content)

    def test_send_graded_result(self):

        payload = {
            'user_id': 'default_user_id',
            'role': 'student',
            'oauth_nonce': '',
            'oauth_timestamp': '',
            'oauth_consumer_key': 'test_client_key',
            'lti_version': 'LTI-1p0',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0',
            'oauth_signature': '',
            'lti_message_type': 'basic-lti-launch-request',
            'oauth_callback': 'about:blank',
            'launch_presentation_return_url': '',
            'lis_outcome_service_url': '',
            'lis_result_sourcedid': '',
            'resource_link_id':'',
        }
        self.server.check_oauth_signature = Mock(return_value=True)
        # This is the uri for sending grade from lti.
        headers = {'referer': 'http://localhost:8000/'}
        response = requests.post(self.uri, data=payload, headers=headers)
        self.assertIn('This is LTI tool. Success.', response.content)
        self.server.grade_data['TC answer'] = "Test response"
        graded_response = requests.post('http://127.0.0.1:8034/grade')
        self.assertIn('Test response', graded_response.content)



