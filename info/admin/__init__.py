from flask import Blueprint
from flask import request
from flask import session,redirect

admin_blue = Blueprint("admin",__name__,url_prefix="/admin")

from . import views

# 后台管理界面只能让管理登陆，普通用户登陆不进来
# 我们就必须在admin文件夹地下进行权限校验
# 如果是管理员才能登陆，如果不是管理员就不能登陆
@admin_blue.before_request
def check_admin():
    is_admin = session.get("is_admin",False)
    if not is_admin and not request.url.endswith("/admin/login"):
        return redirect("/")