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
from iqs_client.api.mms_repository_api import MmsRepositoryApi  # noqa: E501
from iqs_client.rest import ApiException


class TestMmsRepositoryApi(unittest.TestCase):
    """MmsRepositoryApi unit test stubs"""

    def setUp(self):
        self.api = iqs_client.api.mms_repository_api.MmsRepositoryApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_mms_repository_info(self):
        """Test case for get_mms_repository_info

        Get repository structure (orgs, projects, refs, commits)  # noqa: E501
        """
        pass

    def test_get_repository_compartment_details(self):
        """Test case for get_repository_compartment_details

        Retrieve detailed repository structure information for an MMS commit.  # noqa: E501
        """
        pass

    def test_update_mms_repository(self):
        """Test case for update_mms_repository

        Update repository structure from MMS  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
