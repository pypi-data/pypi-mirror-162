# coding: utf-8

"""
    IncQuery Server Web API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: placeHolderApiVersion
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import iqs_client
from iqs_client.models.resource import Resource  # noqa: E501
from iqs_client.rest import ApiException

class TestResource(unittest.TestCase):
    """Resource unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Resource
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.resource.Resource()  # noqa: E501
        if include_optional :
            return Resource(
                resource_id = '3c4be8a2-eb9c-4de0-95ac-e51fc4c27e68', 
                title = 'ICS-ALLQueries.MASTER', 
                branches = [
                    iqs_client.models.branch.Branch(
                        branch_id = '958bd4bb-a145-48bf-a1df-da10803b6233', 
                        title = 'trunk', 
                        revisions = [{"revisionNumer":1}], )
                    ]
            )
        else :
            return Resource(
                resource_id = '3c4be8a2-eb9c-4de0-95ac-e51fc4c27e68',
                branches = [
                    iqs_client.models.branch.Branch(
                        branch_id = '958bd4bb-a145-48bf-a1df-da10803b6233', 
                        title = 'trunk', 
                        revisions = [{"revisionNumer":1}], )
                    ],
        )

    def testResource(self):
        """Test Resource"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
