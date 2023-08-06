# coding: utf-8

import re
import six



from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class UpdateCloudWafServer:

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'front_protocol': 'str',
        'back_protocol': 'str',
        'address': 'str',
        'port': 'int',
        'type': 'str'
    }

    attribute_map = {
        'front_protocol': 'front_protocol',
        'back_protocol': 'back_protocol',
        'address': 'address',
        'port': 'port',
        'type': 'type'
    }

    def __init__(self, front_protocol=None, back_protocol=None, address=None, port=None, type=None):
        """UpdateCloudWafServer

        The model defined in huaweicloud sdk

        :param front_protocol: 对外协议
        :type front_protocol: str
        :param back_protocol: 源站协议
        :type back_protocol: str
        :param address: 源站地址
        :type address: str
        :param port: 源站端口
        :type port: int
        :param type: 源站地址为ipv4或ipv6
        :type type: str
        """
        
        

        self._front_protocol = None
        self._back_protocol = None
        self._address = None
        self._port = None
        self._type = None
        self.discriminator = None

        if front_protocol is not None:
            self.front_protocol = front_protocol
        if back_protocol is not None:
            self.back_protocol = back_protocol
        if address is not None:
            self.address = address
        if port is not None:
            self.port = port
        if type is not None:
            self.type = type

    @property
    def front_protocol(self):
        """Gets the front_protocol of this UpdateCloudWafServer.

        对外协议

        :return: The front_protocol of this UpdateCloudWafServer.
        :rtype: str
        """
        return self._front_protocol

    @front_protocol.setter
    def front_protocol(self, front_protocol):
        """Sets the front_protocol of this UpdateCloudWafServer.

        对外协议

        :param front_protocol: The front_protocol of this UpdateCloudWafServer.
        :type front_protocol: str
        """
        self._front_protocol = front_protocol

    @property
    def back_protocol(self):
        """Gets the back_protocol of this UpdateCloudWafServer.

        源站协议

        :return: The back_protocol of this UpdateCloudWafServer.
        :rtype: str
        """
        return self._back_protocol

    @back_protocol.setter
    def back_protocol(self, back_protocol):
        """Sets the back_protocol of this UpdateCloudWafServer.

        源站协议

        :param back_protocol: The back_protocol of this UpdateCloudWafServer.
        :type back_protocol: str
        """
        self._back_protocol = back_protocol

    @property
    def address(self):
        """Gets the address of this UpdateCloudWafServer.

        源站地址

        :return: The address of this UpdateCloudWafServer.
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this UpdateCloudWafServer.

        源站地址

        :param address: The address of this UpdateCloudWafServer.
        :type address: str
        """
        self._address = address

    @property
    def port(self):
        """Gets the port of this UpdateCloudWafServer.

        源站端口

        :return: The port of this UpdateCloudWafServer.
        :rtype: int
        """
        return self._port

    @port.setter
    def port(self, port):
        """Sets the port of this UpdateCloudWafServer.

        源站端口

        :param port: The port of this UpdateCloudWafServer.
        :type port: int
        """
        self._port = port

    @property
    def type(self):
        """Gets the type of this UpdateCloudWafServer.

        源站地址为ipv4或ipv6

        :return: The type of this UpdateCloudWafServer.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this UpdateCloudWafServer.

        源站地址为ipv4或ipv6

        :param type: The type of this UpdateCloudWafServer.
        :type type: str
        """
        self._type = type

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
        if not isinstance(other, UpdateCloudWafServer):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
