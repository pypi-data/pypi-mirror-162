# coding: utf-8

"""
    FINBOURNE Identity Service API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.0.1809
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from finbourne_identity.configuration import Configuration


class RoleResponse(object):
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
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'id': 'str',
        'role_id': 'RoleId',
        'source': 'str',
        'name': 'str',
        'description': 'str'
    }

    attribute_map = {
        'id': 'id',
        'role_id': 'roleId',
        'source': 'source',
        'name': 'name',
        'description': 'description'
    }

    required_map = {
        'id': 'required',
        'role_id': 'required',
        'source': 'required',
        'name': 'required',
        'description': 'optional'
    }

    def __init__(self, id=None, role_id=None, source=None, name=None, description=None, local_vars_configuration=None):  # noqa: E501
        """RoleResponse - a model defined in OpenAPI"
        
        :param id:  The role's system supplied unique identifier (required)
        :type id: str
        :param role_id:  (required)
        :type role_id: finbourne_identity.RoleId
        :param source:  The source of the role (required)
        :type source: str
        :param name:  The role name, which must be unique within the system. (required)
        :type name: str
        :param description:  The description for this role
        :type description: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._role_id = None
        self._source = None
        self._name = None
        self._description = None
        self.discriminator = None

        self.id = id
        self.role_id = role_id
        self.source = source
        self.name = name
        self.description = description

    @property
    def id(self):
        """Gets the id of this RoleResponse.  # noqa: E501

        The role's system supplied unique identifier  # noqa: E501

        :return: The id of this RoleResponse.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this RoleResponse.

        The role's system supplied unique identifier  # noqa: E501

        :param id: The id of this RoleResponse.  # noqa: E501
        :type id: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def role_id(self):
        """Gets the role_id of this RoleResponse.  # noqa: E501


        :return: The role_id of this RoleResponse.  # noqa: E501
        :rtype: finbourne_identity.RoleId
        """
        return self._role_id

    @role_id.setter
    def role_id(self, role_id):
        """Sets the role_id of this RoleResponse.


        :param role_id: The role_id of this RoleResponse.  # noqa: E501
        :type role_id: finbourne_identity.RoleId
        """
        if self.local_vars_configuration.client_side_validation and role_id is None:  # noqa: E501
            raise ValueError("Invalid value for `role_id`, must not be `None`")  # noqa: E501

        self._role_id = role_id

    @property
    def source(self):
        """Gets the source of this RoleResponse.  # noqa: E501

        The source of the role  # noqa: E501

        :return: The source of this RoleResponse.  # noqa: E501
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this RoleResponse.

        The source of the role  # noqa: E501

        :param source: The source of this RoleResponse.  # noqa: E501
        :type source: str
        """
        if self.local_vars_configuration.client_side_validation and source is None:  # noqa: E501
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501

        self._source = source

    @property
    def name(self):
        """Gets the name of this RoleResponse.  # noqa: E501

        The role name, which must be unique within the system.  # noqa: E501

        :return: The name of this RoleResponse.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this RoleResponse.

        The role name, which must be unique within the system.  # noqa: E501

        :param name: The name of this RoleResponse.  # noqa: E501
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def description(self):
        """Gets the description of this RoleResponse.  # noqa: E501

        The description for this role  # noqa: E501

        :return: The description of this RoleResponse.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this RoleResponse.

        The description for this role  # noqa: E501

        :param description: The description of this RoleResponse.  # noqa: E501
        :type description: str
        """

        self._description = description

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, RoleResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RoleResponse):
            return True

        return self.to_dict() != other.to_dict()
