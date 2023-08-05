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


class EnvironmentVariableCopy(object):
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
        'source_deployment': 'str',
        'source_version': 'str'
    }

    attribute_map = {
        'source_deployment': 'source_deployment',
        'source_version': 'source_version'
    }

    def __init__(self, source_deployment=None, source_version=None, local_vars_configuration=None, **kwargs):  # noqa: E501
        """EnvironmentVariableCopy - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._source_deployment = None
        self._source_version = None
        self.discriminator = None

        self.source_deployment = source_deployment
        if source_version is not None:
            self.source_version = source_version

    @property
    def source_deployment(self):
        """Gets the source_deployment of this EnvironmentVariableCopy.  # noqa: E501


        :return: The source_deployment of this EnvironmentVariableCopy.  # noqa: E501
        :rtype: str
        """
        return self._source_deployment

    @source_deployment.setter
    def source_deployment(self, source_deployment):
        """Sets the source_deployment of this EnvironmentVariableCopy.


        :param source_deployment: The source_deployment of this EnvironmentVariableCopy.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and source_deployment is None:  # noqa: E501
            raise ValueError("Invalid value for `source_deployment`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                source_deployment is not None and not isinstance(source_deployment, str)):
            raise ValueError("Parameter `source_deployment` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                source_deployment is not None and len(source_deployment) < 1):
            raise ValueError("Invalid value for `source_deployment`, length must be greater than or equal to `1`")  # noqa: E501

        self._source_deployment = source_deployment

    @property
    def source_version(self):
        """Gets the source_version of this EnvironmentVariableCopy.  # noqa: E501


        :return: The source_version of this EnvironmentVariableCopy.  # noqa: E501
        :rtype: str
        """
        return self._source_version

    @source_version.setter
    def source_version(self, source_version):
        """Sets the source_version of this EnvironmentVariableCopy.


        :param source_version: The source_version of this EnvironmentVariableCopy.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                source_version is not None and not isinstance(source_version, str)):
            raise ValueError("Parameter `source_version` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                source_version is not None and len(source_version) < 1):
            raise ValueError("Invalid value for `source_version`, length must be greater than or equal to `1`")  # noqa: E501

        self._source_version = source_version

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
        if not isinstance(other, EnvironmentVariableCopy):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EnvironmentVariableCopy):
            return True

        return self.to_dict() != other.to_dict()
