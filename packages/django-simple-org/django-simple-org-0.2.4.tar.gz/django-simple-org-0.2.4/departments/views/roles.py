# -*- coding : utf-8 -*-
"""
@File        : role.py
@Author      : liushuo
@Time        : 2022/5/25 4:20 PM
@Description :
"""
from django.db import transaction

from departments.common.config import BadRequestCode, ServerErrorCode
from departments.utils.error_response import Resp

from departments.utils.role_funcs import (
    create_role,
    get_roles,
    get_role_object,
    update_role,
    delete_role,
    get_role_user,
    add_role_user,
    delete_role_user,
    user_change_role,
    edit_role,
)


class RoleControl(object):

    def __init__(self, organization_id: int):
        if not isinstance(organization_id, int):
            raise TypeError(f"organization_id is failed type")
        self.organization_id = organization_id

    @transaction.atomic
    def create(self, data: dict):
        """
        创建角色
        :param data: {"name": "角色名称", "desc": "角色备注"}
        :return:
        """
        data["organization_id"] = self.organization_id
        try:
            return create_role(data)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    def list(self, role_name: str = None):
        """
        获取组织下的角色信息
        :param role_name:
        :return:
        """

        try:
            return get_roles(self.organization_id, role_name)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    def retrieve(self, pk: int):
        """
        获取某一个角色的信息
        :param pk:
        :return:
        """
        return get_role_object(self.organization_id, pk)

    @transaction.atomic
    def update(self, pk: int, data: dict):
        """
        修改某一个角色的信息
        :param pk:
        :param data:
        :return:
        """
        data["organization_id"] = self.organization_id
        try:
            return update_role(pk, data)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    @transaction.atomic
    def delete(self, pk: int):
        """
        删除某一个角色
        :param pk:
        :return:
        """
        return delete_role(self.organization_id, pk)

    @transaction.atomic
    def edit(self, pk: int):
        """
        停用该角色
        :param pk:
        :return:
        """
        return edit_role(self.organization_id, pk)

    @transaction.atomic
    def create_role_user(self, role_id, user_ids: list):
        """
        角色中添加用户（批量添加）
        :param role_id:
        :param user_ids:
        :return:
        """
        try:
            return add_role_user(self.organization_id, role_id, user_ids)
        except Exception as err:
            return Resp(code=BadRequestCode, msg=str(err))

    # def role_user_list(self, role_id, page: int, size: int):
    def role_user_list(self, role_id):
        """
        获取角色对应的用户
        :param role_id:角色的code
        :param page:
        :param size:
        :return:
        """
        """
        部门是根据id查的，为什么角色不可以用id查
        """
        return get_role_user(self.organization_id, role_id)

    @transaction.atomic
    def change(self, user_id: int, role_ids: list):
        """
        用户修改角色
        """
        try:
            return user_change_role(self.organization_id, user_id, role_ids)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg=str(err))

    @transaction.atomic
    def delete_role_user(self, role_id, user_ids: list):
        """
        移除对应角色的用户（批量移除）
        :param role_id:
        :param user_ids:
        :return:
        """
        return delete_role_user(self.organization_id, role_id, user_ids)

