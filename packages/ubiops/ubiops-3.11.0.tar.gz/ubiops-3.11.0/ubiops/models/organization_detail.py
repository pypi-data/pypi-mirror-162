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


class OrganizationDetail(object):
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
        'id': 'str',
        'name': 'str',
        'creation_date': 'datetime',
        'subscription': 'str',
        'status': 'str',
        'subscription_self_service': 'bool'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'creation_date': 'creation_date',
        'subscription': 'subscription',
        'status': 'status',
        'subscription_self_service': 'subscription_self_service'
    }

    def __init__(self, id=None, name=None, creation_date=None, subscription=None, status=None, subscription_self_service=None, local_vars_configuration=None, **kwargs):  # noqa: E501
        """OrganizationDetail - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._creation_date = None
        self._subscription = None
        self._status = None
        self._subscription_self_service = None
        self.discriminator = None

        if id is not None:
            self.id = id
        self.name = name
        if creation_date is not None:
            self.creation_date = creation_date
        if subscription is not None:
            self.subscription = subscription
        self.status = status
        if subscription_self_service is not None:
            self.subscription_self_service = subscription_self_service

    @property
    def id(self):
        """Gets the id of this OrganizationDetail.  # noqa: E501


        :return: The id of this OrganizationDetail.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OrganizationDetail.


        :param id: The id of this OrganizationDetail.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                id is not None and not isinstance(id, str)):
            raise ValueError("Parameter `id` must be a string")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this OrganizationDetail.  # noqa: E501


        :return: The name of this OrganizationDetail.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this OrganizationDetail.


        :param name: The name of this OrganizationDetail.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and not isinstance(name, str)):
            raise ValueError("Parameter `name` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 64):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) < 1):
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def creation_date(self):
        """Gets the creation_date of this OrganizationDetail.  # noqa: E501


        :return: The creation_date of this OrganizationDetail.  # noqa: E501
        :rtype: datetime
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this OrganizationDetail.


        :param creation_date: The creation_date of this OrganizationDetail.  # noqa: E501
        :type: datetime
        """

        self._creation_date = creation_date

    @property
    def subscription(self):
        """Gets the subscription of this OrganizationDetail.  # noqa: E501


        :return: The subscription of this OrganizationDetail.  # noqa: E501
        :rtype: str
        """
        return self._subscription

    @subscription.setter
    def subscription(self, subscription):
        """Sets the subscription of this OrganizationDetail.


        :param subscription: The subscription of this OrganizationDetail.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                subscription is not None and not isinstance(subscription, str)):
            raise ValueError("Parameter `subscription` must be a string")  # noqa: E501

        self._subscription = subscription

    @property
    def status(self):
        """Gets the status of this OrganizationDetail.  # noqa: E501


        :return: The status of this OrganizationDetail.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this OrganizationDetail.


        :param status: The status of this OrganizationDetail.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and status is None:  # noqa: E501
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                status is not None and not isinstance(status, str)):
            raise ValueError("Parameter `status` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                status is not None and len(status) < 1):
            raise ValueError("Invalid value for `status`, length must be greater than or equal to `1`")  # noqa: E501

        self._status = status

    @property
    def subscription_self_service(self):
        """Gets the subscription_self_service of this OrganizationDetail.  # noqa: E501


        :return: The subscription_self_service of this OrganizationDetail.  # noqa: E501
        :rtype: bool
        """
        return self._subscription_self_service

    @subscription_self_service.setter
    def subscription_self_service(self, subscription_self_service):
        """Sets the subscription_self_service of this OrganizationDetail.


        :param subscription_self_service: The subscription_self_service of this OrganizationDetail.  # noqa: E501
        :type: bool
        """
        if (self.local_vars_configuration.client_side_validation and
                subscription_self_service is not None and not isinstance(subscription_self_service, bool)):
            raise ValueError("Parameter `subscription_self_service` must be a boolean")  # noqa: E501

        self._subscription_self_service = subscription_self_service

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
        if not isinstance(other, OrganizationDetail):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OrganizationDetail):
            return True

        return self.to_dict() != other.to_dict()
