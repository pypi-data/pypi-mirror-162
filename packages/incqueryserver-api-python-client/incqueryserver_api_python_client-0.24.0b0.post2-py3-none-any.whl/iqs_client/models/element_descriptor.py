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


class ElementDescriptor(object):
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
        'element_id': 'str',
        'revision_number': 'int',
        'branch_id': 'str',
        'resource_id': 'str',
        'workspace_id': 'str'
    }

    attribute_map = {
        'element_id': 'elementId',
        'revision_number': 'revisionNumber',
        'branch_id': 'branchId',
        'resource_id': 'resourceId',
        'workspace_id': 'workspaceId'
    }

    def __init__(self, element_id=None, revision_number=None, branch_id=None, resource_id=None, workspace_id=None, local_vars_configuration=None):  # noqa: E501
        """ElementDescriptor - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._element_id = None
        self._revision_number = None
        self._branch_id = None
        self._resource_id = None
        self._workspace_id = None
        self.discriminator = None

        self.element_id = element_id
        self.revision_number = revision_number
        self.branch_id = branch_id
        self.resource_id = resource_id
        self.workspace_id = workspace_id

    @property
    def element_id(self):
        """Gets the element_id of this ElementDescriptor.  # noqa: E501


        :return: The element_id of this ElementDescriptor.  # noqa: E501
        :rtype: str
        """
        return self._element_id

    @element_id.setter
    def element_id(self, element_id):
        """Sets the element_id of this ElementDescriptor.


        :param element_id: The element_id of this ElementDescriptor.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and element_id is None:  # noqa: E501
            raise ValueError("Invalid value for `element_id`, must not be `None`")  # noqa: E501

        self._element_id = element_id

    @property
    def revision_number(self):
        """Gets the revision_number of this ElementDescriptor.  # noqa: E501


        :return: The revision_number of this ElementDescriptor.  # noqa: E501
        :rtype: int
        """
        return self._revision_number

    @revision_number.setter
    def revision_number(self, revision_number):
        """Sets the revision_number of this ElementDescriptor.


        :param revision_number: The revision_number of this ElementDescriptor.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and revision_number is None:  # noqa: E501
            raise ValueError("Invalid value for `revision_number`, must not be `None`")  # noqa: E501

        self._revision_number = revision_number

    @property
    def branch_id(self):
        """Gets the branch_id of this ElementDescriptor.  # noqa: E501


        :return: The branch_id of this ElementDescriptor.  # noqa: E501
        :rtype: str
        """
        return self._branch_id

    @branch_id.setter
    def branch_id(self, branch_id):
        """Sets the branch_id of this ElementDescriptor.


        :param branch_id: The branch_id of this ElementDescriptor.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and branch_id is None:  # noqa: E501
            raise ValueError("Invalid value for `branch_id`, must not be `None`")  # noqa: E501

        self._branch_id = branch_id

    @property
    def resource_id(self):
        """Gets the resource_id of this ElementDescriptor.  # noqa: E501


        :return: The resource_id of this ElementDescriptor.  # noqa: E501
        :rtype: str
        """
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id):
        """Sets the resource_id of this ElementDescriptor.


        :param resource_id: The resource_id of this ElementDescriptor.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and resource_id is None:  # noqa: E501
            raise ValueError("Invalid value for `resource_id`, must not be `None`")  # noqa: E501

        self._resource_id = resource_id

    @property
    def workspace_id(self):
        """Gets the workspace_id of this ElementDescriptor.  # noqa: E501


        :return: The workspace_id of this ElementDescriptor.  # noqa: E501
        :rtype: str
        """
        return self._workspace_id

    @workspace_id.setter
    def workspace_id(self, workspace_id):
        """Sets the workspace_id of this ElementDescriptor.


        :param workspace_id: The workspace_id of this ElementDescriptor.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and workspace_id is None:  # noqa: E501
            raise ValueError("Invalid value for `workspace_id`, must not be `None`")  # noqa: E501

        self._workspace_id = workspace_id

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
        if not isinstance(other, ElementDescriptor):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ElementDescriptor):
            return True

        return self.to_dict() != other.to_dict()
