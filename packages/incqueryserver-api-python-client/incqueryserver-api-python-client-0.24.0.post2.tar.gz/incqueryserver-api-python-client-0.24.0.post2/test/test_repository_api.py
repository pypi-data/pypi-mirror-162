# coding: utf-8

"""
    IncQuery Server Web API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: placeHolderApiVersion
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import iqs_client
from iqs_client.api.repository_api import RepositoryApi  # noqa: E501
from iqs_client.rest import ApiException


class TestRepositoryApi(unittest.TestCase):
    """RepositoryApi unit test stubs"""

    def setUp(self):
        self.api = iqs_client.api.repository_api.RepositoryApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_repository_info(self):
        """Test case for get_repository_info

        Get repository structure (workspaces, resources, branches, revisions)  # noqa: E501
        """
        pass

    def test_get_repository_revision_details(self):
        """Test case for get_repository_revision_details

        Retrieve detailed repository structure information for a revision  # noqa: E501
        """
        pass

    def test_update_repository(self):
        """Test case for update_repository

        Update repository structure from TWC  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
