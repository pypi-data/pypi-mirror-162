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
from iqs_client.models.compartment_operation_states_response import CompartmentOperationStatesResponse  # noqa: E501
from iqs_client.rest import ApiException

class TestCompartmentOperationStatesResponse(unittest.TestCase):
    """CompartmentOperationStatesResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test CompartmentOperationStatesResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.compartment_operation_states_response.CompartmentOperationStatesResponse()  # noqa: E501
        if include_optional :
            return CompartmentOperationStatesResponse(
                states = {
                    'key' : iqs_client.models.compartment_operation_state.CompartmentOperationState(
                        progress = iqs_client.models.compartment_operation_progress.CompartmentOperationProgress(
                            estimated_time_remaining = 0, 
                            total_units_of_work = 0, 
                            completed_units_of_work = 0, 
                            tracked = True, ), 
                        state = iqs_client.models.compartment_operation_state_details.CompartmentOperationStateDetails(
                            message = iqs_client.models.message.message(), 
                            operation_state = 'TERMINATED', ), )
                    }
            )
        else :
            return CompartmentOperationStatesResponse(
        )

    def testCompartmentOperationStatesResponse(self):
        """Test CompartmentOperationStatesResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
