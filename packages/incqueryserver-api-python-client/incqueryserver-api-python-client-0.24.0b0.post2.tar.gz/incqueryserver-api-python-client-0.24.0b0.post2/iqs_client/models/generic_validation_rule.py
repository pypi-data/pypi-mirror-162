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


class GenericValidationRule(object):
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
        'constraint': 'TypedElementInCompartmentDescriptor',
        'severity': 'str',
        'matching_elements': 'list[GenericValidationMatchingElement]'
    }

    attribute_map = {
        'constraint': 'constraint',
        'severity': 'severity',
        'matching_elements': 'matchingElements'
    }

    def __init__(self, constraint=None, severity=None, matching_elements=None, local_vars_configuration=None):  # noqa: E501
        """GenericValidationRule - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._constraint = None
        self._severity = None
        self._matching_elements = None
        self.discriminator = None

        self.constraint = constraint
        self.severity = severity
        self.matching_elements = matching_elements

    @property
    def constraint(self):
        """Gets the constraint of this GenericValidationRule.  # noqa: E501


        :return: The constraint of this GenericValidationRule.  # noqa: E501
        :rtype: TypedElementInCompartmentDescriptor
        """
        return self._constraint

    @constraint.setter
    def constraint(self, constraint):
        """Sets the constraint of this GenericValidationRule.


        :param constraint: The constraint of this GenericValidationRule.  # noqa: E501
        :type: TypedElementInCompartmentDescriptor
        """
        if self.local_vars_configuration.client_side_validation and constraint is None:  # noqa: E501
            raise ValueError("Invalid value for `constraint`, must not be `None`")  # noqa: E501

        self._constraint = constraint

    @property
    def severity(self):
        """Gets the severity of this GenericValidationRule.  # noqa: E501


        :return: The severity of this GenericValidationRule.  # noqa: E501
        :rtype: str
        """
        return self._severity

    @severity.setter
    def severity(self, severity):
        """Sets the severity of this GenericValidationRule.


        :param severity: The severity of this GenericValidationRule.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and severity is None:  # noqa: E501
            raise ValueError("Invalid value for `severity`, must not be `None`")  # noqa: E501
        allowed_values = ["info", "debug", "warning", "error", "fatal"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and severity not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `severity` ({0}), must be one of {1}"  # noqa: E501
                .format(severity, allowed_values)
            )

        self._severity = severity

    @property
    def matching_elements(self):
        """Gets the matching_elements of this GenericValidationRule.  # noqa: E501


        :return: The matching_elements of this GenericValidationRule.  # noqa: E501
        :rtype: list[GenericValidationMatchingElement]
        """
        return self._matching_elements

    @matching_elements.setter
    def matching_elements(self, matching_elements):
        """Sets the matching_elements of this GenericValidationRule.


        :param matching_elements: The matching_elements of this GenericValidationRule.  # noqa: E501
        :type: list[GenericValidationMatchingElement]
        """
        if self.local_vars_configuration.client_side_validation and matching_elements is None:  # noqa: E501
            raise ValueError("Invalid value for `matching_elements`, must not be `None`")  # noqa: E501

        self._matching_elements = matching_elements

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
        if not isinstance(other, GenericValidationRule):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GenericValidationRule):
            return True

        return self.to_dict() != other.to_dict()
