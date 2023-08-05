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


class ImpactAnalysisResult(object):
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
        'result_size': 'int',
        'resource_statistics': 'ImpactAnalysisResourceStatistics',
        'model_compartments': 'list[ModelCompartmentWithDependentElements]'
    }

    attribute_map = {
        'result_size': 'resultSize',
        'resource_statistics': 'resourceStatistics',
        'model_compartments': 'modelCompartments'
    }

    def __init__(self, result_size=None, resource_statistics=None, model_compartments=None, local_vars_configuration=None):  # noqa: E501
        """ImpactAnalysisResult - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._result_size = None
        self._resource_statistics = None
        self._model_compartments = None
        self.discriminator = None

        self.result_size = result_size
        self.resource_statistics = resource_statistics
        self.model_compartments = model_compartments

    @property
    def result_size(self):
        """Gets the result_size of this ImpactAnalysisResult.  # noqa: E501


        :return: The result_size of this ImpactAnalysisResult.  # noqa: E501
        :rtype: int
        """
        return self._result_size

    @result_size.setter
    def result_size(self, result_size):
        """Sets the result_size of this ImpactAnalysisResult.


        :param result_size: The result_size of this ImpactAnalysisResult.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and result_size is None:  # noqa: E501
            raise ValueError("Invalid value for `result_size`, must not be `None`")  # noqa: E501

        self._result_size = result_size

    @property
    def resource_statistics(self):
        """Gets the resource_statistics of this ImpactAnalysisResult.  # noqa: E501


        :return: The resource_statistics of this ImpactAnalysisResult.  # noqa: E501
        :rtype: ImpactAnalysisResourceStatistics
        """
        return self._resource_statistics

    @resource_statistics.setter
    def resource_statistics(self, resource_statistics):
        """Sets the resource_statistics of this ImpactAnalysisResult.


        :param resource_statistics: The resource_statistics of this ImpactAnalysisResult.  # noqa: E501
        :type: ImpactAnalysisResourceStatistics
        """
        if self.local_vars_configuration.client_side_validation and resource_statistics is None:  # noqa: E501
            raise ValueError("Invalid value for `resource_statistics`, must not be `None`")  # noqa: E501

        self._resource_statistics = resource_statistics

    @property
    def model_compartments(self):
        """Gets the model_compartments of this ImpactAnalysisResult.  # noqa: E501


        :return: The model_compartments of this ImpactAnalysisResult.  # noqa: E501
        :rtype: list[ModelCompartmentWithDependentElements]
        """
        return self._model_compartments

    @model_compartments.setter
    def model_compartments(self, model_compartments):
        """Sets the model_compartments of this ImpactAnalysisResult.


        :param model_compartments: The model_compartments of this ImpactAnalysisResult.  # noqa: E501
        :type: list[ModelCompartmentWithDependentElements]
        """
        if self.local_vars_configuration.client_side_validation and model_compartments is None:  # noqa: E501
            raise ValueError("Invalid value for `model_compartments`, must not be `None`")  # noqa: E501

        self._model_compartments = model_compartments

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
        if not isinstance(other, ImpactAnalysisResult):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImpactAnalysisResult):
            return True

        return self.to_dict() != other.to_dict()
