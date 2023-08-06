# coding: utf-8

import re
import six


from huaweicloudsdkcore.sdk_response import SdkResponse
from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class ShowCompositeHostResponse(SdkResponse):

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
        'proxy': 'bool',
        'timestamp': 'int',
        'paid_type': 'str',
        'flag': 'HostFlag',
        'waf_type': 'str'
    }

    attribute_map = {
        'id': 'id',
        'hostname': 'hostname',
        'policyid': 'policyid',
        'access_code': 'access_code',
        'protect_status': 'protect_status',
        'access_status': 'access_status',
        'proxy': 'proxy',
        'timestamp': 'timestamp',
        'paid_type': 'paid_type',
        'flag': 'flag',
        'waf_type': 'waf_type'
    }

    def __init__(self, id=None, hostname=None, policyid=None, access_code=None, protect_status=None, access_status=None, proxy=None, timestamp=None, paid_type=None, flag=None, waf_type=None):
        """ShowCompositeHostResponse

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
        :param proxy: 是否开启了代理
        :type proxy: bool
        :param timestamp: 创建防护域名的时间
        :type timestamp: int
        :param paid_type: 套餐付费模式，目前只支持prePaid预付款模式
        :type paid_type: str
        :param flag: 
        :type flag: :class:`huaweicloudsdkwaf.v1.HostFlag`
        :param waf_type: 域名所属WAF模式,cloud为云模式，premium为独享模式
        :type waf_type: str
        """
        
        super(ShowCompositeHostResponse, self).__init__()

        self._id = None
        self._hostname = None
        self._policyid = None
        self._access_code = None
        self._protect_status = None
        self._access_status = None
        self._proxy = None
        self._timestamp = None
        self._paid_type = None
        self._flag = None
        self._waf_type = None
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
        if proxy is not None:
            self.proxy = proxy
        if timestamp is not None:
            self.timestamp = timestamp
        if paid_type is not None:
            self.paid_type = paid_type
        if flag is not None:
            self.flag = flag
        if waf_type is not None:
            self.waf_type = waf_type

    @property
    def id(self):
        """Gets the id of this ShowCompositeHostResponse.

        域名id

        :return: The id of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ShowCompositeHostResponse.

        域名id

        :param id: The id of this ShowCompositeHostResponse.
        :type id: str
        """
        self._id = id

    @property
    def hostname(self):
        """Gets the hostname of this ShowCompositeHostResponse.

        创建的云模式防护域名

        :return: The hostname of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        """Sets the hostname of this ShowCompositeHostResponse.

        创建的云模式防护域名

        :param hostname: The hostname of this ShowCompositeHostResponse.
        :type hostname: str
        """
        self._hostname = hostname

    @property
    def policyid(self):
        """Gets the policyid of this ShowCompositeHostResponse.

        策略id

        :return: The policyid of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._policyid

    @policyid.setter
    def policyid(self, policyid):
        """Sets the policyid of this ShowCompositeHostResponse.

        策略id

        :param policyid: The policyid of this ShowCompositeHostResponse.
        :type policyid: str
        """
        self._policyid = policyid

    @property
    def access_code(self):
        """Gets the access_code of this ShowCompositeHostResponse.

        cname前缀

        :return: The access_code of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._access_code

    @access_code.setter
    def access_code(self, access_code):
        """Sets the access_code of this ShowCompositeHostResponse.

        cname前缀

        :param access_code: The access_code of this ShowCompositeHostResponse.
        :type access_code: str
        """
        self._access_code = access_code

    @property
    def protect_status(self):
        """Gets the protect_status of this ShowCompositeHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :return: The protect_status of this ShowCompositeHostResponse.
        :rtype: int
        """
        return self._protect_status

    @protect_status.setter
    def protect_status(self, protect_status):
        """Sets the protect_status of this ShowCompositeHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :param protect_status: The protect_status of this ShowCompositeHostResponse.
        :type protect_status: int
        """
        self._protect_status = protect_status

    @property
    def access_status(self):
        """Gets the access_status of this ShowCompositeHostResponse.

        接入状态

        :return: The access_status of this ShowCompositeHostResponse.
        :rtype: int
        """
        return self._access_status

    @access_status.setter
    def access_status(self, access_status):
        """Sets the access_status of this ShowCompositeHostResponse.

        接入状态

        :param access_status: The access_status of this ShowCompositeHostResponse.
        :type access_status: int
        """
        self._access_status = access_status

    @property
    def proxy(self):
        """Gets the proxy of this ShowCompositeHostResponse.

        是否开启了代理

        :return: The proxy of this ShowCompositeHostResponse.
        :rtype: bool
        """
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        """Sets the proxy of this ShowCompositeHostResponse.

        是否开启了代理

        :param proxy: The proxy of this ShowCompositeHostResponse.
        :type proxy: bool
        """
        self._proxy = proxy

    @property
    def timestamp(self):
        """Gets the timestamp of this ShowCompositeHostResponse.

        创建防护域名的时间

        :return: The timestamp of this ShowCompositeHostResponse.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this ShowCompositeHostResponse.

        创建防护域名的时间

        :param timestamp: The timestamp of this ShowCompositeHostResponse.
        :type timestamp: int
        """
        self._timestamp = timestamp

    @property
    def paid_type(self):
        """Gets the paid_type of this ShowCompositeHostResponse.

        套餐付费模式，目前只支持prePaid预付款模式

        :return: The paid_type of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._paid_type

    @paid_type.setter
    def paid_type(self, paid_type):
        """Sets the paid_type of this ShowCompositeHostResponse.

        套餐付费模式，目前只支持prePaid预付款模式

        :param paid_type: The paid_type of this ShowCompositeHostResponse.
        :type paid_type: str
        """
        self._paid_type = paid_type

    @property
    def flag(self):
        """Gets the flag of this ShowCompositeHostResponse.


        :return: The flag of this ShowCompositeHostResponse.
        :rtype: :class:`huaweicloudsdkwaf.v1.HostFlag`
        """
        return self._flag

    @flag.setter
    def flag(self, flag):
        """Sets the flag of this ShowCompositeHostResponse.


        :param flag: The flag of this ShowCompositeHostResponse.
        :type flag: :class:`huaweicloudsdkwaf.v1.HostFlag`
        """
        self._flag = flag

    @property
    def waf_type(self):
        """Gets the waf_type of this ShowCompositeHostResponse.

        域名所属WAF模式,cloud为云模式，premium为独享模式

        :return: The waf_type of this ShowCompositeHostResponse.
        :rtype: str
        """
        return self._waf_type

    @waf_type.setter
    def waf_type(self, waf_type):
        """Sets the waf_type of this ShowCompositeHostResponse.

        域名所属WAF模式,cloud为云模式，premium为独享模式

        :param waf_type: The waf_type of this ShowCompositeHostResponse.
        :type waf_type: str
        """
        self._waf_type = waf_type

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
        if not isinstance(other, ShowCompositeHostResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
