import os
import logging
import requests

from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status, exceptions

from test.settings import api_settings
from .keycloak import get_keycloak_openid

log = logging.getLogger('drf_keycloak_auth')


class UserLoginTestCase(APITestCase):

    # def setUp(self):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.client = APIClient(raise_request_exception=False)

    def test_login_authentication(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer '
            + self.__get_token(get_keycloak_openid())
        )
        response = self.client.get('/test_auth/')

        # log.debug(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_authentication_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'bad-token')
        response = self.client.get('/test_auth/')

        self.assertRaises(exceptions.AuthenticationFailed)

    def test_login_multi_authentication(self):
        keycloak_openid = get_keycloak_openid(
            api_settings.KEYCLOAK_MULTI_OIDC_JSON[0])

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.__get_token(keycloak_openid))
        response = self.client.get('/test_auth_multi_oidc/')

        # log.debug(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_multi_authentication_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'bad-token')
        response = self.client.get('/test_auth_multi_oidc/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_multi_authentication_no_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + '')
        response = self.client.get('/test_auth_multi_oidc/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_user_has_admin_role(self):
    #     pass

    def __get_token(self, keycloak_openid):
        response = requests.post(
            f'{keycloak_openid.connection.base_url}realms/'
            f'{keycloak_openid.realm_name}/protocol/openid-connect/token',
            data={
                'client_id': {keycloak_openid.client_id},
                'client_secret': {keycloak_openid.client_secret_key},
                'grant_type': 'password',
                'username': os.getenv('TEST_USERNAME'),
                'password': os.getenv('TEST_PASSWORD')
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
        )

        log.debug(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['access_token'])

        return response.json()['access_token']
