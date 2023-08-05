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


class UserPendingCreate(object):
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
        'email': 'str',
        'password': 'str',
        'name': 'str',
        'surname': 'str',
        'terms_conditions': 'bool',
        'newsletter': 'bool'
    }

    attribute_map = {
        'email': 'email',
        'password': 'password',
        'name': 'name',
        'surname': 'surname',
        'terms_conditions': 'terms_conditions',
        'newsletter': 'newsletter'
    }

    def __init__(self, email=None, password=None, name=None, surname=None, terms_conditions=None, newsletter=None, local_vars_configuration=None, **kwargs):  # noqa: E501
        """UserPendingCreate - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._email = None
        self._password = None
        self._name = None
        self._surname = None
        self._terms_conditions = None
        self._newsletter = None
        self.discriminator = None

        self.email = email
        self.password = password
        self.name = name
        self.surname = surname
        self.terms_conditions = terms_conditions
        if newsletter is not None:
            self.newsletter = newsletter

    @property
    def email(self):
        """Gets the email of this UserPendingCreate.  # noqa: E501


        :return: The email of this UserPendingCreate.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this UserPendingCreate.


        :param email: The email of this UserPendingCreate.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and email is None:  # noqa: E501
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                email is not None and not isinstance(email, str)):
            raise ValueError("Parameter `email` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                email is not None and len(email) > 254):
            raise ValueError("Invalid value for `email`, length must be less than or equal to `254`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                email is not None and len(email) < 1):
            raise ValueError("Invalid value for `email`, length must be greater than or equal to `1`")  # noqa: E501

        self._email = email

    @property
    def password(self):
        """Gets the password of this UserPendingCreate.  # noqa: E501


        :return: The password of this UserPendingCreate.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this UserPendingCreate.


        :param password: The password of this UserPendingCreate.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and password is None:  # noqa: E501
            raise ValueError("Invalid value for `password`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                password is not None and not isinstance(password, str)):
            raise ValueError("Parameter `password` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                password is not None and len(password) > 128):
            raise ValueError("Invalid value for `password`, length must be less than or equal to `128`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                password is not None and len(password) < 1):
            raise ValueError("Invalid value for `password`, length must be greater than or equal to `1`")  # noqa: E501

        self._password = password

    @property
    def name(self):
        """Gets the name of this UserPendingCreate.  # noqa: E501


        :return: The name of this UserPendingCreate.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UserPendingCreate.


        :param name: The name of this UserPendingCreate.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and not isinstance(name, str)):
            raise ValueError("Parameter `name` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 256):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `256`")  # noqa: E501

        self._name = name

    @property
    def surname(self):
        """Gets the surname of this UserPendingCreate.  # noqa: E501


        :return: The surname of this UserPendingCreate.  # noqa: E501
        :rtype: str
        """
        return self._surname

    @surname.setter
    def surname(self, surname):
        """Sets the surname of this UserPendingCreate.


        :param surname: The surname of this UserPendingCreate.  # noqa: E501
        :type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                surname is not None and not isinstance(surname, str)):
            raise ValueError("Parameter `surname` must be a string")  # noqa: E501

        if (self.local_vars_configuration.client_side_validation and
                surname is not None and len(surname) > 256):
            raise ValueError("Invalid value for `surname`, length must be less than or equal to `256`")  # noqa: E501

        self._surname = surname

    @property
    def terms_conditions(self):
        """Gets the terms_conditions of this UserPendingCreate.  # noqa: E501


        :return: The terms_conditions of this UserPendingCreate.  # noqa: E501
        :rtype: bool
        """
        return self._terms_conditions

    @terms_conditions.setter
    def terms_conditions(self, terms_conditions):
        """Sets the terms_conditions of this UserPendingCreate.


        :param terms_conditions: The terms_conditions of this UserPendingCreate.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and terms_conditions is None:  # noqa: E501
            raise ValueError("Invalid value for `terms_conditions`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                terms_conditions is not None and not isinstance(terms_conditions, bool)):
            raise ValueError("Parameter `terms_conditions` must be a boolean")  # noqa: E501

        self._terms_conditions = terms_conditions

    @property
    def newsletter(self):
        """Gets the newsletter of this UserPendingCreate.  # noqa: E501


        :return: The newsletter of this UserPendingCreate.  # noqa: E501
        :rtype: bool
        """
        return self._newsletter

    @newsletter.setter
    def newsletter(self, newsletter):
        """Sets the newsletter of this UserPendingCreate.


        :param newsletter: The newsletter of this UserPendingCreate.  # noqa: E501
        :type: bool
        """
        if (self.local_vars_configuration.client_side_validation and
                newsletter is not None and not isinstance(newsletter, bool)):
            raise ValueError("Parameter `newsletter` must be a boolean")  # noqa: E501

        self._newsletter = newsletter

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
        if not isinstance(other, UserPendingCreate):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserPendingCreate):
            return True

        return self.to_dict() != other.to_dict()
