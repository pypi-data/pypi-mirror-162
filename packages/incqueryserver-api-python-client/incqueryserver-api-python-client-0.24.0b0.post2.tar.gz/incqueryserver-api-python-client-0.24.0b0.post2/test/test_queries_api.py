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
from iqs_client.api.queries_api import QueriesApi  # noqa: E501
from iqs_client.rest import ApiException


class TestQueriesApi(unittest.TestCase):
    """QueriesApi unit test stubs"""

    def setUp(self):
        self.api = iqs_client.api.queries_api.QueriesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_query_details(self):
        """Test case for get_query_details

        Retrieve detailed information for a query specification  # noqa: E501
        """
        pass

    def test_list_queries(self):
        """Test case for list_queries

        List registered query specifications  # noqa: E501
        """
        pass

    def test_register_queries(self):
        """Test case for register_queries

        Register query definitions  # noqa: E501
        """
        pass

    def test_register_queries_from_model(self):
        """Test case for register_queries_from_model

        Registers query definitions contained in models uploaded to TWC  # noqa: E501
        """
        pass

    def test_register_queries_from_model_compartment(self):
        """Test case for register_queries_from_model_compartment

        Registers query definitions contained in model compartments.  # noqa: E501
        """
        pass

    def test_register_queries_plain_text(self):
        """Test case for register_queries_plain_text

        Register query definitions in plain text format  # noqa: E501
        """
        pass

    def test_unregister_all_queries(self):
        """Test case for unregister_all_queries

        Unregister all queries  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
