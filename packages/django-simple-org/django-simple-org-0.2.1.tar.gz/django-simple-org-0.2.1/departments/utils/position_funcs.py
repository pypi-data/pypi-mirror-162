# -*- coding : utf-8 -*-
"""
@File        : position_funcs.py
@Author      : liushuo
@Time        : 2022/5/30 11:13 AM
@Description :
"""

from django.db import transaction

from departments.common.config import BadRequestCode, ServerErrorCode
from departments.models import Position, UserPosition
from departments.forms.forms import PositionForms
from departments.utils.error_response import Resp


def create_position(data: dict) -> dict:
    """
    创建岗位
    :param data:
    :return:
    """
    # 校验数据的合法性
    checked = PositionForms(data)
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg=checked.errors)
    # 查找表里面有没有这个岗位名称，如果有的话，不能添加
    same_position = Position.objects.filter(
        name=data["name"],
        organization_id=data["organization_id"]
    )
    if same_position:
        return Resp(code=ServerErrorCode, msg=f"[{data['name']}]在当前组织中已经存在，请使用其他名称")
    position_instance = Position.objects.create(**data)
    return Resp(data={'id': position_instance.pk})


def get_position(organization_id: int, position_name: str = None):
    """
    获取全部的部门
    :param organization_id:
    :param position_name:
    :return:
    """
    position_items = list()
    # 没有搜索部门名字的时候
    if not position_name:
        instance = Position.objects.filter(
            organization_id=organization_id,
            is_deleted=False
        )
        for i in instance:
            position_items.append({
                "id": i.id,
                "name": i.name,
                "desc": i.desc,
                "created_at": i.created_at
            })
    # 有搜索部门名称的时候
    else:
        instance = Position.objects.get(
            organization_id=organization_id,
            is_deleted=False,
            name__contains=position_name.strip()
        )
        position_items = {
            "id": instance.id,
            "name": instance.name,
            "desc": instance.desc,
            "created_at": instance.created_at
        }
    return Resp(data=position_items)


def retrieve_position(organization_id: int, pk: int):
    """
    获取某个岗位的信息
    :param organization_id:
    :param pk:
    :return:
    """
    try:
        instance = Position.objects.get(
            pk=pk,
            organization_id=organization_id,
            is_deleted=False
        )
        return Resp(
            data={"id": instance.id, "name": instance.name, "desc": instance.desc}
        )
    except Position.DoesNotExist:
        return Resp(code=ServerErrorCode, msg=f"the position can't be found id: {pk}")


@transaction.atomic
def update_position(pk: int, data: dict):
    """
    修改岗位的信息
    :param pk:
    :param data:
    :return:
    """
    """
    先去查询，然后看看是不是创建者，创者者不可编辑，删除，所以不能修改
    """
    # 检查需要修改的数据的合法性
    checked = PositionForms(data)
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg=checked.errors)
    organization_id = data["organization_id"]
    try:
        instance = Position.objects.get(
            pk=pk,
            organization_id=organization_id,
            is_deleted=False
        )
        if not instance.is_edited:
            return Resp(code=BadRequestCode, msg="系统岗位，不可修改")
        instance.name = data["name"]
        instance.desc = data["desc"]
        instance.save()
        return Resp(data="修改成功")
    except Exception as err:
        raise ValueError(f"{str(err)} id: {pk}")


def delete_position(organization_id: int, pk: int):
    """
    删除岗位
    :param organization_id:
    :param pk:
    :return:
    """
    instance = Position.objects.get(
        pk=pk,
        organization_id=organization_id,
        is_deleted=False
    )
    if not instance.is_edited:
        return Resp(code=BadRequestCode, msg="系统岗位，不可删除")
    if UserPosition.objects.filter(
            position_id=pk
    ).exists():
        return Resp(data=f"该岗位下有用户，不可删除")

    Position.objects.filter(pk=pk).update(is_deleted=True)  # delete()
    return Resp(data="删除成功")


def add_position_user(organization_id: int, position_id: int, user_ids: list):
    """
    批量添加岗位下的用户
    :param organization_id:
    :param position_id:
    :param user_ids:
    :return:
    """
    """
    先去组织下去查找这个岗位，如果有的话，去添加，
    这个地方用搜索吗？
    下拉框的话，直接就看出有多少岗位来了，就不用查询岗位存不存在了
    """
    if not Position.objects.filter(
            organization_id=organization_id,
            pk=position_id
    ).exists():
        return Resp(code=BadRequestCode, msg="当前组织下没有该岗位")
    position_user_list = [
        UserPosition(position_id=position_id, user_id=user) for user in user_ids
    ]
    try:
        UserPosition.objects.bulk_create(position_user_list)
        return Resp(data="添加成功")
    except Exception as err:
        raise Exception(err)


def get_position_user(organization_id: int, position_id: int):
    """
    获取岗位下的所有用户
    :param organization_id:
    :param position_id:
    :return:
    """
    user_ids = UserPosition.objects.filter(
        position__organization_id=organization_id,
        position__is_deleted=False,
        position_id=position_id,
    ).order_by("id").values_list("user_id", flat=True)
    return Resp(data=list(user_ids))


def delete_position_user(organization_id: int, position_id: int, user_ids: list):
    """
    批量删除岗位下的用户
    :param organization_id:
    :param position_id:
    :param user_ids:
    :return:
    """
    """
    需要查询吗？有没有搜索框？
    """
    if not Position.objects.filter(
        organization_id=organization_id,
        pk=position_id
    ).exists():
        return Resp(code=BadRequestCode, msg="当前组织没有该岗位")
    UserPosition.objects.filter(
        position__organization_id=organization_id,
        position_id=position_id,
        user_id__in=user_ids
    ).delete()
    return Resp(data="删除成功")


@transaction.atomic
def user_change_position(organization_id: int, user_id: int, position_ids: list):
    """
    用户变更岗位
    :param organization_id:
    :param user_id:
    :param position_ids:
    :return:
    """
    try:
        valid_position_count = Position.objects.filter(
            id__in=position_ids,
            organization_id=organization_id
        ).count()
        if not valid_position_count == len(position_ids):
            raise ValueError("参数错误")
        UserPosition.objects.filter(
            position__organization_id=organization_id,
            user_id=user_id
        ).delete()

        changed_instance_list = [UserPosition(position_id=id_, user_id=user_id) for id_ in position_ids]
        UserPosition.objects.bulk_create(changed_instance_list)
        return Resp()
    except Exception as e:
        raise Exception(str(e))


