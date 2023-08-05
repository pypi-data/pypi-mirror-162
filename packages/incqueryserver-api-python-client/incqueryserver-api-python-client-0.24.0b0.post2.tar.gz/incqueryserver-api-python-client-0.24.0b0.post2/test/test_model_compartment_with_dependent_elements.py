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
from iqs_client.models.model_compartment_with_dependent_elements import ModelCompartmentWithDependentElements  # noqa: E501
from iqs_client.rest import ApiException

class TestModelCompartmentWithDependentElements(unittest.TestCase):
    """ModelCompartmentWithDependentElements unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ModelCompartmentWithDependentElements
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.model_compartment_with_dependent_elements.ModelCompartmentWithDependentElements()  # noqa: E501
        if include_optional :
            return ModelCompartmentWithDependentElements(
                model_compartment = {"compartmentURI":"mms-index:/orgs/iql/projects/PROJECT-d0c236d9-186a-485c-9c67-9e6693d1f0d8/refs/master/commits/bc1d4c28-f777-4f58-9df3-b856f39d928f"}, 
                model_compartment_details = iqs_client.models.model_compartment_details.ModelCompartmentDetails(
                    repository_path = 'IQL / Example Project / master', 
                    author = 'Administrator', 
                    details = null, ), 
                references = [
                    iqs_client.models.dependent_element_in_compartment_descriptor.DependentElementInCompartmentDescriptor(
                        reference = iqs_client.models.feature_descriptor_proxy.FeatureDescriptorProxy(
                            feature_name = '0', 
                            feature_kind = 'EATTRIBUTE', 
                            classifier_proxy = iqs_client.models.e_classifier_descriptor.EClassifierDescriptor(
                                classifier_name = '0', 
                                package_ns_uri = '0', ), ), 
                        elements = [
                            iqs_client.models.dependent_element_details.DependentElementDetails(
                                name = 'Dependency1', 
                                element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                element_link = 'https://127.0.0.1:8111/osmc/workspaces/2394f5d1-1321-4f34-a373-cc1b159c7ebd/resources/34cc77c8-d3ef-40a6-9b91-65786117fe67/branches/bd03a239-7836-4d4c-9bcb-eba73b001b1e/revisions/1/elements/85827022-a8b5-4e6e-b604-9b7417cc7713', )
                            ], )
                    ]
            )
        else :
            return ModelCompartmentWithDependentElements(
                model_compartment = {"compartmentURI":"mms-index:/orgs/iql/projects/PROJECT-d0c236d9-186a-485c-9c67-9e6693d1f0d8/refs/master/commits/bc1d4c28-f777-4f58-9df3-b856f39d928f"},
                references = [
                    iqs_client.models.dependent_element_in_compartment_descriptor.DependentElementInCompartmentDescriptor(
                        reference = iqs_client.models.feature_descriptor_proxy.FeatureDescriptorProxy(
                            feature_name = '0', 
                            feature_kind = 'EATTRIBUTE', 
                            classifier_proxy = iqs_client.models.e_classifier_descriptor.EClassifierDescriptor(
                                classifier_name = '0', 
                                package_ns_uri = '0', ), ), 
                        elements = [
                            iqs_client.models.dependent_element_details.DependentElementDetails(
                                name = 'Dependency1', 
                                element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                element_link = 'https://127.0.0.1:8111/osmc/workspaces/2394f5d1-1321-4f34-a373-cc1b159c7ebd/resources/34cc77c8-d3ef-40a6-9b91-65786117fe67/branches/bd03a239-7836-4d4c-9bcb-eba73b001b1e/revisions/1/elements/85827022-a8b5-4e6e-b604-9b7417cc7713', )
                            ], )
                    ],
        )

    def testModelCompartmentWithDependentElements(self):
        """Test ModelCompartmentWithDependentElements"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
