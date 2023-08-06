# -*- coding : utf-8 -*-
"""
@File        : position.py
@Author      : liushuo
@Time        : 2022/5/30 11:13 AM
@Description :
"""
from django.db import transaction

from departments.common.config import ServerErrorCode, BadRequestCode
from departments.utils.error_response import Resp
from departments.utils.position_funcs import (
    create_position,
    get_position,
    retrieve_position,
    update_position,
    delete_position,
    add_position_user,
    get_position_user,
    delete_position_user,
    user_change_position
)


class PositionViewSet(object):

    def __init__(self, organization_id: int):
        if not isinstance(organization_id, int):
            raise TypeError(f"organization_id is failed type")
        self.organization_id = organization_id

    @transaction.atomic
    def create(self, data: dict):
        """
        创建岗位
        :param data:{"name": "岗位名称", "desc"： "岗位描述"}
        :return:
        """
        data["organization_id"] = self.organization_id
        return create_position(data)
        # return create_position(self.organization_id, data)

    def list(self, position_name: str = None):
        """
        获取全部的角色
        :param position_name:
        :return:
        """
        try:
            return get_position(self.organization_id, position_name)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    def retrieve(self, pk: int):
        """
        获取某个部门的详情
        :param pk:
        :return:
        """
        return retrieve_position(self.organization_id, pk)

    @transaction.atomic
    def update(self, pk: int, data: dict):
        """
        修改岗位信息
        :param pk:
        :param data:
        :return:
        """
        data["organization_id"] = self.organization_id
        try:
            return update_position(pk, data)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    @transaction.atomic
    def delete(self, pk: int):
        """
        删除岗位
        :param pk:
        :return:
        """
        return delete_position(self.organization_id, pk)

    @transaction.atomic
    def create_position_user(self, position_id: int, user_ids: list):
        """
        添加岗位用户（批量添加）
        :param position_id:岗位id
        :param user_ids: 用户id
        :return:
        """
        try:
            return add_position_user(self.organization_id, position_id, user_ids)
        except Exception as err:
            return Resp(code=BadRequestCode, msg=str(err))

    @transaction.atomic
    def change(self, user_id: int, position_ids: list):
        """
        用户变更岗位
        """
        try:
            return user_change_position(self.organization_id, user_id, position_ids)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    def position_user_list(self, position_id):
        """
        获取岗位下的所有用户
        :param position_id:
        :return:
        """
        return get_position_user(self.organization_id, position_id)

    @transaction.atomic
    def delete_position_user(self, position_id: int, user_ids: list):
        """
        批量删除岗位下的用户
        :param position_id:
        :param user_ids:
        :return:
        """
        return delete_position_user(self.organization_id, position_id, user_ids)


