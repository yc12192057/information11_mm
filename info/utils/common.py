from flask import g
from flask import session

from info.models import User
import functools

def index_class(index):
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""

# 装饰器的使用，装饰器这么好用的啊～～
#　用装饰器对功能进行封装，装饰器也不就是个函数么…………然后在需要使用的地方直接使用装饰器实现，避免重复搬砖哦　
def user_login_data(f):
    # 以下装饰器避免修改被装饰者的属性
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        # TODO 根据登陆时设置的session查询用户是否登陆
        user_id = session.get("user_id")
        # 默认值
        user = None
        if user_id:
            # 根据id查询当前用户
            user = User.query.get(user_id)
            # 查询出来的是ｕｓｅｒ对象
            print("nininin你你你您你少年张三丰",user,"wowowowowoowowowo我我我我我")
        g.user = user
        return f(*args,**kwargs)
    return wrapper




# def user_login_data(f):
#     @functools.wraps(f)
#     def wrapper(*args, **kwargs):
#         user_id = session.get("user_id")
#         user = None
#         if user_id:
#             user = User.query.get(user_id)
#         g.user = user
#         return f(*args, **kwargs)
#     return wrapper



# def user_login_data():
#     """
#         右上角的用户判断是否登陆
#         :param news_id:
#         :return:
#         """
#     # 获取到用户id
#     user_id = session.get("user_id")
#     # 默认值
#     user = None
#     if user_id:
#         # 根据id查询当前用户
#         user = User.query.get(user_id)
#     return user