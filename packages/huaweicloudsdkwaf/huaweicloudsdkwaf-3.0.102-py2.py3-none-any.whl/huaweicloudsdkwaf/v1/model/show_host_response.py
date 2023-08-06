# coding: utf-8

import re
import six


from huaweicloudsdkcore.sdk_response import SdkResponse
from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class ShowHostResponse(SdkResponse):

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
        'hostname': 'str',
        'policyid': 'str',
        'access_code': 'str',
        'protect_status': 'int',
        'access_status': 'int',
        'protocol': 'str',
        'certificateid': 'str',
        'certificatename': 'str',
        'server': 'list[CloudWafServer]',
        'proxy': 'bool',
        'timestamp': 'int',
        'exclusive_ip': 'bool',
        'timeout_config': 'TimeoutConfig'
    }

    attribute_map = {
        'id': 'id',
        'hostname': 'hostname',
        'policyid': 'policyid',
        'access_code': 'access_code',
        'protect_status': 'protect_status',
        'access_status': 'access_status',
        'protocol': 'protocol',
        'certificateid': 'certificateid',
        'certificatename': 'certificatename',
        'server': 'server',
        'proxy': 'proxy',
        'timestamp': 'timestamp',
        'exclusive_ip': 'exclusive_ip',
        'timeout_config': 'timeout_config'
    }

    def __init__(self, id=None, hostname=None, policyid=None, access_code=None, protect_status=None, access_status=None, protocol=None, certificateid=None, certificatename=None, server=None, proxy=None, timestamp=None, exclusive_ip=None, timeout_config=None):
        """ShowHostResponse

        The model defined in huaweicloud sdk

        :param id: 域名id
        :type id: str
        :param hostname: 创建的云模式防护域名
        :type hostname: str
        :param policyid: 策略id
        :type policyid: str
        :param access_code: cname前缀
        :type access_code: str
        :param protect_status: 域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测
        :type protect_status: int
        :param access_status: 接入状态
        :type access_status: int
        :param protocol: 后端包含的协议类型：HTTPS、HTTP、HTTP&amp;HTTPS
        :type protocol: str
        :param certificateid: https证书id
        :type certificateid: str
        :param certificatename: 证书名称
        :type certificatename: str
        :param server: 源站信息
        :type server: list[:class:`huaweicloudsdkwaf.v1.CloudWafServer`]
        :param proxy: 是否开启了代理
        :type proxy: bool
        :param timestamp: 创建防护域名的时间
        :type timestamp: int
        :param exclusive_ip: 是否使用独享ip
        :type exclusive_ip: bool
        :param timeout_config: 
        :type timeout_config: :class:`huaweicloudsdkwaf.v1.TimeoutConfig`
        """
        
        super(ShowHostResponse, self).__init__()

        self._id = None
        self._hostname = None
        self._policyid = None
        self._access_code = None
        self._protect_status = None
        self._access_status = None
        self._protocol = None
        self._certificateid = None
        self._certificatename = None
        self._server = None
        self._proxy = None
        self._timestamp = None
        self._exclusive_ip = None
        self._timeout_config = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if hostname is not None:
            self.hostname = hostname
        if policyid is not None:
            self.policyid = policyid
        if access_code is not None:
            self.access_code = access_code
        if protect_status is not None:
            self.protect_status = protect_status
        if access_status is not None:
            self.access_status = access_status
        if protocol is not None:
            self.protocol = protocol
        if certificateid is not None:
            self.certificateid = certificateid
        if certificatename is not None:
            self.certificatename = certificatename
        if server is not None:
            self.server = server
        if proxy is not None:
            self.proxy = proxy
        if timestamp is not None:
            self.timestamp = timestamp
        if exclusive_ip is not None:
            self.exclusive_ip = exclusive_ip
        if timeout_config is not None:
            self.timeout_config = timeout_config

    @property
    def id(self):
        """Gets the id of this ShowHostResponse.

        域名id

        :return: The id of this ShowHostResponse.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ShowHostResponse.

        域名id

        :param id: The id of this ShowHostResponse.
        :type id: str
        """
        self._id = id

    @property
    def hostname(self):
        """Gets the hostname of this ShowHostResponse.

        创建的云模式防护域名

        :return: The hostname of this ShowHostResponse.
        :rtype: str
        """
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        """Sets the hostname of this ShowHostResponse.

        创建的云模式防护域名

        :param hostname: The hostname of this ShowHostResponse.
        :type hostname: str
        """
        self._hostname = hostname

    @property
    def policyid(self):
        """Gets the policyid of this ShowHostResponse.

        策略id

        :return: The policyid of this ShowHostResponse.
        :rtype: str
        """
        return self._policyid

    @policyid.setter
    def policyid(self, policyid):
        """Sets the policyid of this ShowHostResponse.

        策略id

        :param policyid: The policyid of this ShowHostResponse.
        :type policyid: str
        """
        self._policyid = policyid

    @property
    def access_code(self):
        """Gets the access_code of this ShowHostResponse.

        cname前缀

        :return: The access_code of this ShowHostResponse.
        :rtype: str
        """
        return self._access_code

    @access_code.setter
    def access_code(self, access_code):
        """Sets the access_code of this ShowHostResponse.

        cname前缀

        :param access_code: The access_code of this ShowHostResponse.
        :type access_code: str
        """
        self._access_code = access_code

    @property
    def protect_status(self):
        """Gets the protect_status of this ShowHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :return: The protect_status of this ShowHostResponse.
        :rtype: int
        """
        return self._protect_status

    @protect_status.setter
    def protect_status(self, protect_status):
        """Sets the protect_status of this ShowHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :param protect_status: The protect_status of this ShowHostResponse.
        :type protect_status: int
        """
        self._protect_status = protect_status

    @property
    def access_status(self):
        """Gets the access_status of this ShowHostResponse.

        接入状态

        :return: The access_status of this ShowHostResponse.
        :rtype: int
        """
        return self._access_status

    @access_status.setter
    def access_status(self, access_status):
        """Sets the access_status of this ShowHostResponse.

        接入状态

        :param access_status: The access_status of this ShowHostResponse.
        :type access_status: int
        """
        self._access_status = access_status

    @property
    def protocol(self):
        """Gets the protocol of this ShowHostResponse.

        后端包含的协议类型：HTTPS、HTTP、HTTP&HTTPS

        :return: The protocol of this ShowHostResponse.
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """Sets the protocol of this ShowHostResponse.

        后端包含的协议类型：HTTPS、HTTP、HTTP&HTTPS

        :param protocol: The protocol of this ShowHostResponse.
        :type protocol: str
        """
        self._protocol = protocol

    @property
    def certificateid(self):
        """Gets the certificateid of this ShowHostResponse.

        https证书id

        :return: The certificateid of this ShowHostResponse.
        :rtype: str
        """
        return self._certificateid

    @certificateid.setter
    def certificateid(self, certificateid):
        """Sets the certificateid of this ShowHostResponse.

        https证书id

        :param certificateid: The certificateid of this ShowHostResponse.
        :type certificateid: str
        """
        self._certificateid = certificateid

    @property
    def certificatename(self):
        """Gets the certificatename of this ShowHostResponse.

        证书名称

        :return: The certificatename of this ShowHostResponse.
        :rtype: str
        """
        return self._certificatename

    @certificatename.setter
    def certificatename(self, certificatename):
        """Sets the certificatename of this ShowHostResponse.

        证书名称

        :param certificatename: The certificatename of this ShowHostResponse.
        :type certificatename: str
        """
        self._certificatename = certificatename

    @property
    def server(self):
        """Gets the server of this ShowHostResponse.

        源站信息

        :return: The server of this ShowHostResponse.
        :rtype: list[:class:`huaweicloudsdkwaf.v1.CloudWafServer`]
        """
        return self._server

    @server.setter
    def server(self, server):
        """Sets the server of this ShowHostResponse.

        源站信息

        :param server: The server of this ShowHostResponse.
        :type server: list[:class:`huaweicloudsdkwaf.v1.CloudWafServer`]
        """
        self._server = server

    @property
    def proxy(self):
        """Gets the proxy of this ShowHostResponse.

        是否开启了代理

        :return: The proxy of this ShowHostResponse.
        :rtype: bool
        """
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        """Sets the proxy of this ShowHostResponse.

        是否开启了代理

        :param proxy: The proxy of this ShowHostResponse.
        :type proxy: bool
        """
        self._proxy = proxy

    @property
    def timestamp(self):
        """Gets the timestamp of this ShowHostResponse.

        创建防护域名的时间

        :return: The timestamp of this ShowHostResponse.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this ShowHostResponse.

        创建防护域名的时间

        :param timestamp: The timestamp of this ShowHostResponse.
        :type timestamp: int
        """
        self._timestamp = timestamp

    @property
    def exclusive_ip(self):
        """Gets the exclusive_ip of this ShowHostResponse.

        是否使用独享ip

        :return: The exclusive_ip of this ShowHostResponse.
        :rtype: bool
        """
        return self._exclusive_ip

    @exclusive_ip.setter
    def exclusive_ip(self, exclusive_ip):
        """Sets the exclusive_ip of this ShowHostResponse.

        是否使用独享ip

        :param exclusive_ip: The exclusive_ip of this ShowHostResponse.
        :type exclusive_ip: bool
        """
        self._exclusive_ip = exclusive_ip

    @property
    def timeout_config(self):
        """Gets the timeout_config of this ShowHostResponse.


        :return: The timeout_config of this ShowHostResponse.
        :rtype: :class:`huaweicloudsdkwaf.v1.TimeoutConfig`
        """
        return self._timeout_config

    @timeout_config.setter
    def timeout_config(self, timeout_config):
        """Sets the timeout_config of this ShowHostResponse.


        :param timeout_config: The timeout_config of this ShowHostResponse.
        :type timeout_config: :class:`huaweicloudsdkwaf.v1.TimeoutConfig`
        """
        self._timeout_config = timeout_config

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
        if not isinstance(other, ShowHostResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
