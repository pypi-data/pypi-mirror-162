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


class AuditList(object):
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
        'date': 'str',
        'action': 'str',
        'user': 'str',
        'event': 'str',
        'object_type': 'str',
        'object_name': 'str'
    }

    attribute_map = {
        'id': 'id',
        'date': 'date',
        'action': 'action',
        'user': 'user',
        'event': 'event',
        'object_type': 'object_type',
        'object_name': 'object_name'
    }

    def __init__(self, id=None, date=None, action=None, user=None, event=None, object_type=None, object_name=None, local_vars_configuration=None, **kwargs):  # noqa: E501
        """AuditList - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._date = None
        self._action = None
        self._user = None
        self._event = None
        self._object_type = None
        self._object_name = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if date is not None:
            self.date = date
        self.action = action
        if user is not None:
            self.user = user
        if event is not None:
            self.event = event
        self.object_type = object_type
        if object_name is not None:
            self.object_name = object_name

    @property
    def id(self):
        """Gets the id of this AuditList.  # noqa: E501


        :return: The id of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AuditList.


        :param id: The id of this AuditList.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                id is not None and not isinstance(id, str)):
            raise ValueError("Parameter `id` must be a string")  # noqa: E501

        self._id = id

    @property
    def date(self):
        """Gets the date of this AuditList.  # noqa: E501


        :return: The date of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._date

    @date.setter
    def date(self, date):
        """Sets the date of this AuditList.


        :param date: The date of this AuditList.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                date is not None and not isinstance(date, str)):
            raise ValueError("Parameter `date` must be a string")  # noqa: E501

        self._date = date

    @property
    def action(self):
        """Gets the action of this AuditList.  # noqa: E501


        :return: The action of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this AuditList.


        :param action: The action of this AuditList.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and action is None:  # noqa: E501
            raise ValueError("Invalid value for `action`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                action is not None and not isinstance(action, str)):
            raise ValueError("Parameter `action` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                action is not None and len(action) < 1):
            raise ValueError("Invalid value for `action`, length must be greater than or equal to `1`")  # noqa: E501

        self._action = action

    @property
    def user(self):
        """Gets the user of this AuditList.  # noqa: E501


        :return: The user of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this AuditList.


        :param user: The user of this AuditList.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                user is not None and not isinstance(user, str)):
            raise ValueError("Parameter `user` must be a string")  # noqa: E501

        self._user = user

    @property
    def event(self):
        """Gets the event of this AuditList.  # noqa: E501


        :return: The event of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._event

    @event.setter
    def event(self, event):
        """Sets the event of this AuditList.


        :param event: The event of this AuditList.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                event is not None and not isinstance(event, str)):
            raise ValueError("Parameter `event` must be a string")  # noqa: E501

        self._event = event

    @property
    def object_type(self):
        """Gets the object_type of this AuditList.  # noqa: E501


        :return: The object_type of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._object_type

    @object_type.setter
    def object_type(self, object_type):
        """Sets the object_type of this AuditList.


        :param object_type: The object_type of this AuditList.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and object_type is None:  # noqa: E501
            raise ValueError("Invalid value for `object_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                object_type is not None and not isinstance(object_type, str)):
            raise ValueError("Parameter `object_type` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                object_type is not None and len(object_type) > 64):
            raise ValueError("Invalid value for `object_type`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                object_type is not None and len(object_type) < 1):
            raise ValueError("Invalid value for `object_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._object_type = object_type

    @property
    def object_name(self):
        """Gets the object_name of this AuditList.  # noqa: E501


        :return: The object_name of this AuditList.  # noqa: E501
        :rtype: str
        """
        return self._object_name

    @object_name.setter
    def object_name(self, object_name):
        """Sets the object_name of this AuditList.


        :param object_name: The object_name of this AuditList.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                object_name is not None and not isinstance(object_name, str)):
            raise ValueError("Parameter `object_name` must be a string")  # noqa: E501

        self._object_name = object_name

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
        if not isinstance(other, AuditList):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AuditList):
            return True

        return self.to_dict() != other.to_dict()
