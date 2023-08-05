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
from iqs_client.models.mms_repository_structure import MMSRepositoryStructure  # noqa: E501
from iqs_client.rest import ApiException

class TestMMSRepositoryStructure(unittest.TestCase):
    """MMSRepositoryStructure unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test MMSRepositoryStructure
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.mms_repository_structure.MMSRepositoryStructure()  # noqa: E501
        if include_optional :
            return MMSRepositoryStructure(
                id = '0', 
                title = '0', 
                orgs = [
                    iqs_client.models.mms_organization.MMSOrganization(
                        org_id = '6384a103-766c-46e0-830d-8a3b1f479479', 
                        name = 'IQL', 
                        projects = [
                            iqs_client.models.mms_project.MMSProject(
                                project_id = 'PROJECT-bef4f459-5d90-41fb-bc86-4f6d4ebd2dfd', 
                                name = 'ICS-ALLQueries', 
                                refs = [
                                    iqs_client.models.mms_ref.MMSRef(
                                        ref_id = 'master', 
                                        name = 'master', 
                                        commits = {"commitId":"560d3959-3912-434a-a914-8d039d3c9a06"}, )
                                    ], )
                            ], )
                    ]
            )
        else :
            return MMSRepositoryStructure(
                id = '0',
                title = '0',
                orgs = [
                    iqs_client.models.mms_organization.MMSOrganization(
                        org_id = '6384a103-766c-46e0-830d-8a3b1f479479', 
                        name = 'IQL', 
                        projects = [
                            iqs_client.models.mms_project.MMSProject(
                                project_id = 'PROJECT-bef4f459-5d90-41fb-bc86-4f6d4ebd2dfd', 
                                name = 'ICS-ALLQueries', 
                                refs = [
                                    iqs_client.models.mms_ref.MMSRef(
                                        ref_id = 'master', 
                                        name = 'master', 
                                        commits = {"commitId":"560d3959-3912-434a-a914-8d039d3c9a06"}, )
                                    ], )
                            ], )
                    ],
        )

    def testMMSRepositoryStructure(self):
        """Test MMSRepositoryStructure"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
