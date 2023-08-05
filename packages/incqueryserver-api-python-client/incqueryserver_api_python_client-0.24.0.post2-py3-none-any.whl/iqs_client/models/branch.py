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


class Branch(object):
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
        'branch_id': 'str',
        'title': 'str',
        'revisions': 'list[object]'
    }

    attribute_map = {
        'branch_id': 'branchId',
        'title': 'title',
        'revisions': 'revisions'
    }

    def __init__(self, branch_id=None, title=None, revisions=None, local_vars_configuration=None):  # noqa: E501
        """Branch - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._branch_id = None
        self._title = None
        self._revisions = None
        self.discriminator = None

        self.branch_id = branch_id
        if title is not None:
            self.title = title
        self.revisions = revisions

    @property
    def branch_id(self):
        """Gets the branch_id of this Branch.  # noqa: E501


        :return: The branch_id of this Branch.  # noqa: E501
        :rtype: str
        """
        return self._branch_id

    @branch_id.setter
    def branch_id(self, branch_id):
        """Sets the branch_id of this Branch.


        :param branch_id: The branch_id of this Branch.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and branch_id is None:  # noqa: E501
            raise ValueError("Invalid value for `branch_id`, must not be `None`")  # noqa: E501

        self._branch_id = branch_id

    @property
    def title(self):
        """Gets the title of this Branch.  # noqa: E501


        :return: The title of this Branch.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Branch.


        :param title: The title of this Branch.  # noqa: E501
        :type: str
        """

        self._title = title

    @property
    def revisions(self):
        """Gets the revisions of this Branch.  # noqa: E501


        :return: The revisions of this Branch.  # noqa: E501
        :rtype: list[object]
        """
        return self._revisions

    @revisions.setter
    def revisions(self, revisions):
        """Sets the revisions of this Branch.


        :param revisions: The revisions of this Branch.  # noqa: E501
        :type: list[object]
        """
        if self.local_vars_configuration.client_side_validation and revisions is None:  # noqa: E501
            raise ValueError("Invalid value for `revisions`, must not be `None`")  # noqa: E501

        self._revisions = revisions

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
        if not isinstance(other, Branch):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Branch):
            return True

        return self.to_dict() != other.to_dict()
