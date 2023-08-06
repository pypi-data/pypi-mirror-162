# coding: utf-8

import re
import six


from huaweicloudsdkcore.sdk_response import SdkResponse
from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class DeletePremiumHostResponse(SdkResponse):

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
        'region': 'str',
        'protect_status': 'int',
        'access_status': 'int',
        'flag': 'dict(str, str)',
        'mode': 'str',
        'pool_ids': 'list[str]'
    }

    attribute_map = {
        'id': 'id',
        'hostname': 'hostname',
        'policyid': 'policyid',
        'region': 'region',
        'protect_status': 'protect_status',
        'access_status': 'access_status',
        'flag': 'flag',
        'mode': 'mode',
        'pool_ids': 'pool_ids'
    }

    def __init__(self, id=None, hostname=None, policyid=None, region=None, protect_status=None, access_status=None, flag=None, mode=None, pool_ids=None):
        """DeletePremiumHostResponse

        The model defined in huaweicloud sdk

        :param id: 域名id
        :type id: str
        :param hostname: 域名
        :type hostname: str
        :param policyid: 策略id
        :type policyid: str
        :param region: 区域id
        :type region: str
        :param protect_status: 域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测
        :type protect_status: int
        :param access_status: 接入状态
        :type access_status: int
        :param flag: 特殊标识
        :type flag: dict(str, str)
        :param mode: 特殊模式独享引擎的标识（如elb）
        :type mode: str
        :param pool_ids: 特殊模式域名所属独享引擎组
        :type pool_ids: list[str]
        """
        
        super(DeletePremiumHostResponse, self).__init__()

        self._id = None
        self._hostname = None
        self._policyid = None
        self._region = None
        self._protect_status = None
        self._access_status = None
        self._flag = None
        self._mode = None
        self._pool_ids = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if hostname is not None:
            self.hostname = hostname
        if policyid is not None:
            self.policyid = policyid
        if region is not None:
            self.region = region
        if protect_status is not None:
            self.protect_status = protect_status
        if access_status is not None:
            self.access_status = access_status
        if flag is not None:
            self.flag = flag
        if mode is not None:
            self.mode = mode
        if pool_ids is not None:
            self.pool_ids = pool_ids

    @property
    def id(self):
        """Gets the id of this DeletePremiumHostResponse.

        域名id

        :return: The id of this DeletePremiumHostResponse.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DeletePremiumHostResponse.

        域名id

        :param id: The id of this DeletePremiumHostResponse.
        :type id: str
        """
        self._id = id

    @property
    def hostname(self):
        """Gets the hostname of this DeletePremiumHostResponse.

        域名

        :return: The hostname of this DeletePremiumHostResponse.
        :rtype: str
        """
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        """Sets the hostname of this DeletePremiumHostResponse.

        域名

        :param hostname: The hostname of this DeletePremiumHostResponse.
        :type hostname: str
        """
        self._hostname = hostname

    @property
    def policyid(self):
        """Gets the policyid of this DeletePremiumHostResponse.

        策略id

        :return: The policyid of this DeletePremiumHostResponse.
        :rtype: str
        """
        return self._policyid

    @policyid.setter
    def policyid(self, policyid):
        """Sets the policyid of this DeletePremiumHostResponse.

        策略id

        :param policyid: The policyid of this DeletePremiumHostResponse.
        :type policyid: str
        """
        self._policyid = policyid

    @property
    def region(self):
        """Gets the region of this DeletePremiumHostResponse.

        区域id

        :return: The region of this DeletePremiumHostResponse.
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this DeletePremiumHostResponse.

        区域id

        :param region: The region of this DeletePremiumHostResponse.
        :type region: str
        """
        self._region = region

    @property
    def protect_status(self):
        """Gets the protect_status of this DeletePremiumHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :return: The protect_status of this DeletePremiumHostResponse.
        :rtype: int
        """
        return self._protect_status

    @protect_status.setter
    def protect_status(self, protect_status):
        """Sets the protect_status of this DeletePremiumHostResponse.

        域名防护状态：  - -1：bypass，该域名的请求直接到达其后端服务器，不再经过WAF  - 0：暂停防护，WAF只转发该域名的请求，不做攻击检测  - 1：开启防护，WAF根据您配置的策略进行攻击检测

        :param protect_status: The protect_status of this DeletePremiumHostResponse.
        :type protect_status: int
        """
        self._protect_status = protect_status

    @property
    def access_status(self):
        """Gets the access_status of this DeletePremiumHostResponse.

        接入状态

        :return: The access_status of this DeletePremiumHostResponse.
        :rtype: int
        """
        return self._access_status

    @access_status.setter
    def access_status(self, access_status):
        """Sets the access_status of this DeletePremiumHostResponse.

        接入状态

        :param access_status: The access_status of this DeletePremiumHostResponse.
        :type access_status: int
        """
        self._access_status = access_status

    @property
    def flag(self):
        """Gets the flag of this DeletePremiumHostResponse.

        特殊标识

        :return: The flag of this DeletePremiumHostResponse.
        :rtype: dict(str, str)
        """
        return self._flag

    @flag.setter
    def flag(self, flag):
        """Sets the flag of this DeletePremiumHostResponse.

        特殊标识

        :param flag: The flag of this DeletePremiumHostResponse.
        :type flag: dict(str, str)
        """
        self._flag = flag

    @property
    def mode(self):
        """Gets the mode of this DeletePremiumHostResponse.

        特殊模式独享引擎的标识（如elb）

        :return: The mode of this DeletePremiumHostResponse.
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Sets the mode of this DeletePremiumHostResponse.

        特殊模式独享引擎的标识（如elb）

        :param mode: The mode of this DeletePremiumHostResponse.
        :type mode: str
        """
        self._mode = mode

    @property
    def pool_ids(self):
        """Gets the pool_ids of this DeletePremiumHostResponse.

        特殊模式域名所属独享引擎组

        :return: The pool_ids of this DeletePremiumHostResponse.
        :rtype: list[str]
        """
        return self._pool_ids

    @pool_ids.setter
    def pool_ids(self, pool_ids):
        """Sets the pool_ids of this DeletePremiumHostResponse.

        特殊模式域名所属独享引擎组

        :param pool_ids: The pool_ids of this DeletePremiumHostResponse.
        :type pool_ids: list[str]
        """
        self._pool_ids = pool_ids

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
        if not isinstance(other, DeletePremiumHostResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
