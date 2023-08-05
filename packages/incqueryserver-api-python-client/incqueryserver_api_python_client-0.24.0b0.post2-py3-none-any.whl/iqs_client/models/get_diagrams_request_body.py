# coding: utf-8

"""
    IncQuery Server Web API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: placeHolderApiVersion
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from iqs_client.configuration import Configuration


class GetDiagramsRequestBody(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'element_ids': 'list[str]',
        'compartment_uris': 'list[str]'
    }

    attribute_map = {
        'element_ids': 'elementIds',
        'compartment_uris': 'compartmentUris'
    }

    def __init__(self, element_ids=None, compartment_uris=None, local_vars_configuration=None):  # noqa: E501
        """GetDiagramsRequestBody - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._element_ids = None
        self._compartment_uris = None
        self.discriminator = None

        if element_ids is not None:
            self.element_ids = element_ids
        if compartment_uris is not None:
            self.compartment_uris = compartment_uris

    @property
    def element_ids(self):
        """Gets the element_ids of this GetDiagramsRequestBody.  # noqa: E501


        :return: The element_ids of this GetDiagramsRequestBody.  # noqa: E501
        :rtype: list[str]
        """
        return self._element_ids

    @element_ids.setter
    def element_ids(self, element_ids):
        """Sets the element_ids of this GetDiagramsRequestBody.


        :param element_ids: The element_ids of this GetDiagramsRequestBody.  # noqa: E501
        :type: list[str]
        """

        self._element_ids = element_ids

    @property
    def compartment_uris(self):
        """Gets the compartment_uris of this GetDiagramsRequestBody.  # noqa: E501


        :return: The compartment_uris of this GetDiagramsRequestBody.  # noqa: E501
        :rtype: list[str]
        """
        return self._compartment_uris

    @compartment_uris.setter
    def compartment_uris(self, compartment_uris):
        """Sets the compartment_uris of this GetDiagramsRequestBody.


        :param compartment_uris: The compartment_uris of this GetDiagramsRequestBody.  # noqa: E501
        :type: list[str]
        """

        self._compartment_uris = compartment_uris

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GetDiagramsRequestBody):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GetDiagramsRequestBody):
            return True

        return self.to_dict() != other.to_dict()
