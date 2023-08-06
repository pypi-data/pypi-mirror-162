# encoding: utf-8
"""
@project: djangoModel->Auth
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 小程序SDK
@created_time: 2022/7/7 9:38
"""
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
import jwt
import redis
import requests

from config.config import Config
from ..models import BaseInfo, Auth
from ..utils.model_handle import parse_model


class WechatService:
    wx_login_url = "https://api.weixin.qq.com/sns/jscode2session"
    wx_token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    wx_get_phone_url = "https://api.weixin.qq.com/wxa/business/getuserphonenumber"

    def __init__(self):
        self.login_param = {'appid': Config.getIns().get("xj_user", 'app_id'), 'secret': Config.getIns().get("xj_user", 'secret'), 'grant_type': 'authorization_code'}
        self.redis = redis.Redis(
            host=Config.getIns().get("main", 'redis_host'),
            port=Config.getIns().get("main", 'redis_port'),
            password=Config.getIns().get("main", 'redis_password')
        )

    def get_openid(self, code):
        """
        :param code（openid登录的code）:
        :return:(err,data)
        """
        try:
            response = requests.get(self.wx_login_url, code).json()
            if not response['errcode'] == 0:  # openid 换取失败
                return response['errcode'], response['errmsg']
        except Exception as e:
            return 6445, '请求错误'

    def phone_login(self, code):
        """
        过期续约就是重新登录
        :param code: 换取手机号码的code
        :return:(err,data)
        """
        # code 换取手机号
        url = self.wx_get_phone_url + "?access_token={}".format(self.get_access_token()['access_token'])
        header = {'content-type': 'application/json'}
        response = requests.post(url, json={'code': code}, headers=header).json()
        if not response['errcode'] == 0:
            return response['errmsg'], ""
        phone = response['phone_info']['phoneNumber']
        # 检查是否存在该用户，不存在直接注册
        current_user = BaseInfo.objects.filter(phone=phone).filter()
        current_user = parse_model(current_user)
        if not current_user:
            base_info = {
                'user_name': '',
                'phone': phone,
                'email': '',
                'full_name': '请修改用户名',
            }
            current_user = BaseInfo.objects.create(**base_info)
            current_user = parse_model(current_user)
        current_user = current_user[0]
        # 生成登录token
        token = self.__set_token(current_user.get('id', None), phone)
        # 创建用户登录信息，绑定token
        auth = {
            'user_id': current_user.get('id', None),
            'password': make_password('123456', None, 'pbkdf2_sha1'),
            'plaintext': '123456',
            'token': token,
        }
        Auth.objects.update_or_create({'user_id': current_user.get('id', None)}, **auth)
        return 0, {'token': token, 'user_info': current_user}

    def __set_token(self, user_id, account):
        # 生成过期时间
        expire_timestamp = datetime.utcnow() + timedelta(
            days=int(Config.getIns().get('xj_user', 'EXPIRE_DAY')),
            seconds=int(Config.getIns().get('xj_user', 'EXPIRE_SECOND'))
        )
        # 返回token
        return jwt.encode(
            payload={'user_id': user_id, 'account': account, "exp": expire_timestamp},
            key=Config.getIns().get('xj_user', 'JWT_SECRET_KEY')
        )

    def get_access_token(self):
        access_token = self.redis.get('access_token')
        if access_token:
            ttl = self.redis.ttl('access_token')
            return {"access_token": access_token.decode('utf-8'), 'expires_in': ttl, 'local': True}
        param = {
            'appid': Config.getIns().get("xj_user", 'app_id'),
            'secret': Config.getIns().get("xj_user", 'secret'),
            'grant_type': 'client_credential'
        }
        response = requests.get(self.wx_token_url, param).json()
        if 'access_token' in response.keys():
            self.redis.set('access_token', response['access_token'])
            self.redis.expire('access_token', response['expires_in'])
        return response

    def __del__(self):
        self.redis.close()
