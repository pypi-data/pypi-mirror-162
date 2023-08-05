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


class AnalysisRuleResult(object):
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
        'name': 'str',
        'symbolic_name': 'str',
        'category': 'str',
        'query_fqn': 'str',
        'severity': 'str'
    }

    attribute_map = {
        'name': 'name',
        'symbolic_name': 'symbolicName',
        'category': 'category',
        'query_fqn': 'queryFqn',
        'severity': 'severity'
    }

    def __init__(self, name=None, symbolic_name=None, category=None, query_fqn=None, severity=None, local_vars_configuration=None):  # noqa: E501
        """AnalysisRuleResult - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._symbolic_name = None
        self._category = None
        self._query_fqn = None
        self._severity = None
        self.discriminator = None

        self.name = name
        if symbolic_name is not None:
            self.symbolic_name = symbolic_name
        if category is not None:
            self.category = category
        self.query_fqn = query_fqn
        self.severity = severity

    @property
    def name(self):
        """Gets the name of this AnalysisRuleResult.  # noqa: E501


        :return: The name of this AnalysisRuleResult.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AnalysisRuleResult.


        :param name: The name of this AnalysisRuleResult.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def symbolic_name(self):
        """Gets the symbolic_name of this AnalysisRuleResult.  # noqa: E501


        :return: The symbolic_name of this AnalysisRuleResult.  # noqa: E501
        :rtype: str
        """
        return self._symbolic_name

    @symbolic_name.setter
    def symbolic_name(self, symbolic_name):
        """Sets the symbolic_name of this AnalysisRuleResult.


        :param symbolic_name: The symbolic_name of this AnalysisRuleResult.  # noqa: E501
        :type: str
        """

        self._symbolic_name = symbolic_name

    @property
    def category(self):
        """Gets the category of this AnalysisRuleResult.  # noqa: E501


        :return: The category of this AnalysisRuleResult.  # noqa: E501
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category):
        """Sets the category of this AnalysisRuleResult.


        :param category: The category of this AnalysisRuleResult.  # noqa: E501
        :type: str
        """

        self._category = category

    @property
    def query_fqn(self):
        """Gets the query_fqn of this AnalysisRuleResult.  # noqa: E501


        :return: The query_fqn of this AnalysisRuleResult.  # noqa: E501
        :rtype: str
        """
        return self._query_fqn

    @query_fqn.setter
    def query_fqn(self, query_fqn):
        """Sets the query_fqn of this AnalysisRuleResult.


        :param query_fqn: The query_fqn of this AnalysisRuleResult.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and query_fqn is None:  # noqa: E501
            raise ValueError("Invalid value for `query_fqn`, must not be `None`")  # noqa: E501

        self._query_fqn = query_fqn

    @property
    def severity(self):
        """Gets the severity of this AnalysisRuleResult.  # noqa: E501


        :return: The severity of this AnalysisRuleResult.  # noqa: E501
        :rtype: str
        """
        return self._severity

    @severity.setter
    def severity(self, severity):
        """Sets the severity of this AnalysisRuleResult.


        :param severity: The severity of this AnalysisRuleResult.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and severity is None:  # noqa: E501
            raise ValueError("Invalid value for `severity`, must not be `None`")  # noqa: E501
        allowed_values = ["INFO", "DEBUG", "WARNING", "ERROR", "FATAL"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and severity not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `severity` ({0}), must be one of {1}"  # noqa: E501
                .format(severity, allowed_values)
            )

        self._severity = severity

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
        if not isinstance(other, AnalysisRuleResult):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AnalysisRuleResult):
            return True

        return self.to_dict() != other.to_dict()
