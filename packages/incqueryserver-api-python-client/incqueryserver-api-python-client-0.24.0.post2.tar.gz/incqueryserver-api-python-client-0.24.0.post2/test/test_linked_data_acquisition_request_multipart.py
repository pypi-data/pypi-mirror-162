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
from iqs_client.models.linked_data_acquisition_request_multipart import LinkedDataAcquisitionRequestMultipart  # noqa: E501
from iqs_client.rest import ApiException

class TestLinkedDataAcquisitionRequestMultipart(unittest.TestCase):
    """LinkedDataAcquisitionRequestMultipart unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test LinkedDataAcquisitionRequestMultipart
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = iqs_client.models.linked_data_acquisition_request_multipart.LinkedDataAcquisitionRequestMultipart()  # noqa: E501
        if include_optional :
            return LinkedDataAcquisitionRequestMultipart(
                metadata = iqs_client.models.linked_data_acquisition_request_metadata.LinkedDataAcquisitionRequestMetadata(
                    model_compartment = {"compartmentURI":"mms-index:/orgs/iql/projects/PROJECT-d0c236d9-186a-485c-9c67-9e6693d1f0d8/refs/master/commits/bc1d4c28-f777-4f58-9df3-b856f39d928f"}, 
                    document_metadata_entries = [{"linkedDataFormat":"TURTLE","baseURI":"","documentFileName":"foo.ttl"},{"linkedDataFormat":"RDF_XML","baseURI":"http://example.org","documentFileName":"bar.rdf.xml"}], ), 
                documents = [
                    bytes(b'blah')
                    ]
            )
        else :
            return LinkedDataAcquisitionRequestMultipart(
                metadata = iqs_client.models.linked_data_acquisition_request_metadata.LinkedDataAcquisitionRequestMetadata(
                    model_compartment = {"compartmentURI":"mms-index:/orgs/iql/projects/PROJECT-d0c236d9-186a-485c-9c67-9e6693d1f0d8/refs/master/commits/bc1d4c28-f777-4f58-9df3-b856f39d928f"}, 
                    document_metadata_entries = [{"linkedDataFormat":"TURTLE","baseURI":"","documentFileName":"foo.ttl"},{"linkedDataFormat":"RDF_XML","baseURI":"http://example.org","documentFileName":"bar.rdf.xml"}], ),
        )

    def testLinkedDataAcquisitionRequestMultipart(self):
        """Test LinkedDataAcquisitionRequestMultipart"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
