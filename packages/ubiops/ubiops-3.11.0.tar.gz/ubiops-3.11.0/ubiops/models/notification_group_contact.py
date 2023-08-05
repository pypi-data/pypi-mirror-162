# coding: utf-8

"""
    UbiOps

    Client Library to interact with the UbiOps API.  # noqa: E501

    The version of the OpenAPI document: v2.1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from ubiops.configuration import Configuration


class NotificationGroupContact(object):
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
        'type': 'str',
        'configuration': 'dict(str, str)'
    }

    attribute_map = {
        'type': 'type',
        'configuration': 'configuration'
    }

    def __init__(self, type=None, configuration=None, local_vars_configuration=None, **kwargs):  # noqa: E501
        """NotificationGroupContact - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._configuration = None
        self.discriminator = None

        self.type = type
        self.configuration = configuration

    @property
    def type(self):
        """Gets the type of this NotificationGroupContact.  # noqa: E501


        :return: The type of this NotificationGroupContact.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this NotificationGroupContact.


        :param type: The type of this NotificationGroupContact.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and not isinstance(type, str)):
            raise ValueError("Parameter `type` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) < 1):
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def configuration(self):
        """Gets the configuration of this NotificationGroupContact.  # noqa: E501


        :return: The configuration of this NotificationGroupContact.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._configuration

    @configuration.setter
    def configuration(self, configuration):
        """Sets the configuration of this NotificationGroupContact.


        :param configuration: The configuration of this NotificationGroupContact.  # noqa: E501
        :type: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and configuration is None:  # noqa: E501
            raise ValueError("Invalid value for `configuration`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                configuration is not None and not isinstance(configuration, dict)):
            raise ValueError("Parameter `configuration` must be a dictionary")  # noqa: E501

        self._configuration = configuration

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
        if not isinstance(other, NotificationGroupContact):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, NotificationGroupContact):
            return True

        return self.to_dict() != other.to_dict()
