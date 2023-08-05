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
from iqs_client.models.validation_results import ValidationResults  # noqa: E501
from iqs_client.rest import ApiException

class TestValidationResults(unittest.TestCase):
    """ValidationResults unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ValidationResults
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.validation_results.ValidationResults()  # noqa: E501
        if include_optional :
            return ValidationResults(
                diagnostics = iqs_client.models.validation_diagnostics.ValidationDiagnostics(
                    info = 0, 
                    debug = 0, 
                    warning = 0, 
                    error = 0, 
                    fatal = 0, ), 
                revision = {"revisionNumber":1,"branchId":"bd03a239-7836-4d4c-9bcb-eba73b001b1e","resourceId":"34cc77c8-d3ef-40a6-9b91-65786117fe67","workspaceId":"2394f5d1-1321-4f34-a373-cc1b159c7ebd"}, 
                rules = [
                    iqs_client.models.validation_rule.ValidationRule(
                        constraint = iqs_client.models.typed_element_descriptor.TypedElementDescriptor(
                            element = iqs_client.models.element_descriptor.ElementDescriptor(
                                element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                revision_number = 1, 
                                branch_id = 'bd03a239-7836-4d4c-9bcb-eba73b001b1e', 
                                resource_id = '34cc77c8-d3ef-40a6-9b91-65786117fe67', 
                                workspace_id = '2394f5d1-1321-4f34-a373-cc1b159c7ebd', ), 
                            type = '0', 
                            name = '0', 
                            element_link = '0', ), 
                        severity = 'info', 
                        matching_elements = [
                            iqs_client.models.validation_matching_element.ValidationMatchingElement(
                                message = '0', 
                                matching_element = iqs_client.models.typed_element_descriptor.TypedElementDescriptor(
                                    element = iqs_client.models.element_descriptor.ElementDescriptor(
                                        element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                        revision_number = 1, 
                                        branch_id = 'bd03a239-7836-4d4c-9bcb-eba73b001b1e', 
                                        resource_id = '34cc77c8-d3ef-40a6-9b91-65786117fe67', 
                                        workspace_id = '2394f5d1-1321-4f34-a373-cc1b159c7ebd', ), 
                                    type = '0', 
                                    name = '0', 
                                    element_link = '0', ), )
                            ], )
                    ]
            )
        else :
            return ValidationResults(
                diagnostics = iqs_client.models.validation_diagnostics.ValidationDiagnostics(
                    info = 0, 
                    debug = 0, 
                    warning = 0, 
                    error = 0, 
                    fatal = 0, ),
                revision = {"revisionNumber":1,"branchId":"bd03a239-7836-4d4c-9bcb-eba73b001b1e","resourceId":"34cc77c8-d3ef-40a6-9b91-65786117fe67","workspaceId":"2394f5d1-1321-4f34-a373-cc1b159c7ebd"},
                rules = [
                    iqs_client.models.validation_rule.ValidationRule(
                        constraint = iqs_client.models.typed_element_descriptor.TypedElementDescriptor(
                            element = iqs_client.models.element_descriptor.ElementDescriptor(
                                element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                revision_number = 1, 
                                branch_id = 'bd03a239-7836-4d4c-9bcb-eba73b001b1e', 
                                resource_id = '34cc77c8-d3ef-40a6-9b91-65786117fe67', 
                                workspace_id = '2394f5d1-1321-4f34-a373-cc1b159c7ebd', ), 
                            type = '0', 
                            name = '0', 
                            element_link = '0', ), 
                        severity = 'info', 
                        matching_elements = [
                            iqs_client.models.validation_matching_element.ValidationMatchingElement(
                                message = '0', 
                                matching_element = iqs_client.models.typed_element_descriptor.TypedElementDescriptor(
                                    element = iqs_client.models.element_descriptor.ElementDescriptor(
                                        element_id = '85827022-a8b5-4e6e-b604-9b7417cc7713', 
                                        revision_number = 1, 
                                        branch_id = 'bd03a239-7836-4d4c-9bcb-eba73b001b1e', 
                                        resource_id = '34cc77c8-d3ef-40a6-9b91-65786117fe67', 
                                        workspace_id = '2394f5d1-1321-4f34-a373-cc1b159c7ebd', ), 
                                    type = '0', 
                                    name = '0', 
                                    element_link = '0', ), )
                            ], )
                    ],
        )

    def testValidationResults(self):
        """Test ValidationResults"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
