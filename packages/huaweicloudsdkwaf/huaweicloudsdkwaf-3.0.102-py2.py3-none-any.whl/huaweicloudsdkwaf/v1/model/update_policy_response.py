# coding: utf-8

import re
import six


from huaweicloudsdkcore.sdk_response import SdkResponse
from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class UpdatePolicyResponse(SdkResponse):

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'id': 'str',
        'name': 'str',
        'level': 'int',
        'action': 'PolicyAction',
        'options': 'PolicyOption',
        'hosts': 'list[str]',
        'extend': 'dict(str, str)',
        'timestamp': 'int',
        'full_detection': 'bool',
        'bind_host': 'list[BindHost]'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'level': 'level',
        'action': 'action',
        'options': 'options',
        'hosts': 'hosts',
        'extend': 'extend',
        'timestamp': 'timestamp',
        'full_detection': 'full_detection',
        'bind_host': 'bind_host'
    }

    def __init__(self, id=None, name=None, level=None, action=None, options=None, hosts=None, extend=None, timestamp=None, full_detection=None, bind_host=None):
        """UpdatePolicyResponse

        The model defined in huaweicloud sdk

        :param id: 防护策略id
        :type id: str
        :param name: 防护策略名
        :type name: str
        :param level: 防护等级
        :type level: int
        :param action: 
        :type action: :class:`huaweicloudsdkwaf.v1.PolicyAction`
        :param options: 
        :type options: :class:`huaweicloudsdkwaf.v1.PolicyOption`
        :param hosts: 防护域名的信息
        :type hosts: list[str]
        :param extend: 扩展字段
        :type extend: dict(str, str)
        :param timestamp: 创建防护策略的时间
        :type timestamp: int
        :param full_detection: 精准防护中的检测模式
        :type full_detection: bool
        :param bind_host: 防护域名的信息
        :type bind_host: list[:class:`huaweicloudsdkwaf.v1.BindHost`]
        """
        
        super(UpdatePolicyResponse, self).__init__()

        self._id = None
        self._name = None
        self._level = None
        self._action = None
        self._options = None
        self._hosts = None
        self._extend = None
        self._timestamp = None
        self._full_detection = None
        self._bind_host = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if level is not None:
            self.level = level
        if action is not None:
            self.action = action
        if options is not None:
            self.options = options
        if hosts is not None:
            self.hosts = hosts
        if extend is not None:
            self.extend = extend
        if timestamp is not None:
            self.timestamp = timestamp
        if full_detection is not None:
            self.full_detection = full_detection
        if bind_host is not None:
            self.bind_host = bind_host

    @property
    def id(self):
        """Gets the id of this UpdatePolicyResponse.

        防护策略id

        :return: The id of this UpdatePolicyResponse.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this UpdatePolicyResponse.

        防护策略id

        :param id: The id of this UpdatePolicyResponse.
        :type id: str
        """
        self._id = id

    @property
    def name(self):
        """Gets the name of this UpdatePolicyResponse.

        防护策略名

        :return: The name of this UpdatePolicyResponse.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UpdatePolicyResponse.

        防护策略名

        :param name: The name of this UpdatePolicyResponse.
        :type name: str
        """
        self._name = name

    @property
    def level(self):
        """Gets the level of this UpdatePolicyResponse.

        防护等级

        :return: The level of this UpdatePolicyResponse.
        :rtype: int
        """
        return self._level

    @level.setter
    def level(self, level):
        """Sets the level of this UpdatePolicyResponse.

        防护等级

        :param level: The level of this UpdatePolicyResponse.
        :type level: int
        """
        self._level = level

    @property
    def action(self):
        """Gets the action of this UpdatePolicyResponse.


        :return: The action of this UpdatePolicyResponse.
        :rtype: :class:`huaweicloudsdkwaf.v1.PolicyAction`
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this UpdatePolicyResponse.


        :param action: The action of this UpdatePolicyResponse.
        :type action: :class:`huaweicloudsdkwaf.v1.PolicyAction`
        """
        self._action = action

    @property
    def options(self):
        """Gets the options of this UpdatePolicyResponse.


        :return: The options of this UpdatePolicyResponse.
        :rtype: :class:`huaweicloudsdkwaf.v1.PolicyOption`
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this UpdatePolicyResponse.


        :param options: The options of this UpdatePolicyResponse.
        :type options: :class:`huaweicloudsdkwaf.v1.PolicyOption`
        """
        self._options = options

    @property
    def hosts(self):
        """Gets the hosts of this UpdatePolicyResponse.

        防护域名的信息

        :return: The hosts of this UpdatePolicyResponse.
        :rtype: list[str]
        """
        return self._hosts

    @hosts.setter
    def hosts(self, hosts):
        """Sets the hosts of this UpdatePolicyResponse.

        防护域名的信息

        :param hosts: The hosts of this UpdatePolicyResponse.
        :type hosts: list[str]
        """
        self._hosts = hosts

    @property
    def extend(self):
        """Gets the extend of this UpdatePolicyResponse.

        扩展字段

        :return: The extend of this UpdatePolicyResponse.
        :rtype: dict(str, str)
        """
        return self._extend

    @extend.setter
    def extend(self, extend):
        """Sets the extend of this UpdatePolicyResponse.

        扩展字段

        :param extend: The extend of this UpdatePolicyResponse.
        :type extend: dict(str, str)
        """
        self._extend = extend

    @property
    def timestamp(self):
        """Gets the timestamp of this UpdatePolicyResponse.

        创建防护策略的时间

        :return: The timestamp of this UpdatePolicyResponse.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this UpdatePolicyResponse.

        创建防护策略的时间

        :param timestamp: The timestamp of this UpdatePolicyResponse.
        :type timestamp: int
        """
        self._timestamp = timestamp

    @property
    def full_detection(self):
        """Gets the full_detection of this UpdatePolicyResponse.

        精准防护中的检测模式

        :return: The full_detection of this UpdatePolicyResponse.
        :rtype: bool
        """
        return self._full_detection

    @full_detection.setter
    def full_detection(self, full_detection):
        """Sets the full_detection of this UpdatePolicyResponse.

        精准防护中的检测模式

        :param full_detection: The full_detection of this UpdatePolicyResponse.
        :type full_detection: bool
        """
        self._full_detection = full_detection

    @property
    def bind_host(self):
        """Gets the bind_host of this UpdatePolicyResponse.

        防护域名的信息

        :return: The bind_host of this UpdatePolicyResponse.
        :rtype: list[:class:`huaweicloudsdkwaf.v1.BindHost`]
        """
        return self._bind_host

    @bind_host.setter
    def bind_host(self, bind_host):
        """Sets the bind_host of this UpdatePolicyResponse.

        防护域名的信息

        :param bind_host: The bind_host of this UpdatePolicyResponse.
        :type bind_host: list[:class:`huaweicloudsdkwaf.v1.BindHost`]
        """
        self._bind_host = bind_host

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
                if attr in self.sensitive_list:
                    result[attr] = "****"
                else:
                    result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        import simplejson as json
        if six.PY2:
            import sys
            reload(sys)
            sys.setdefaultencoding("utf-8")
        return json.dumps(sanitize_for_serialization(self), ensure_ascii=False)

    def __repr__(self):
        """For `print`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UpdatePolicyResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
