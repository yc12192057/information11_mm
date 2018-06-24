from flask import current_app
from flask import g
from flask import request
from flask import session
from info.utils.image_storage import storage
from info import constants
from info import db
from info.models import Category, News
from info.utils.response_code import RET
from . import profile_blue
from flask import render_template,redirect,jsonify
from info.utils.common import user_login_data
from info.utils.image_storage import storage

@profile_blue.route("/news_list")
@user_login_data
def news_list():
    page = request.args.get("p",1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    paginate = News.query.filter(News.user_id == user.id).paginate(page,2,False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_list =  []
    for item in items:
        news_list.append(item.to_review_dict())

    data = {
        "current_page":current_page,
        "total_page":total_page,
        "news_list":news_list
    }

    return render_template("news/user_news_list.html",data = data)






@profile_blue.route("/news_release",methods = ["GET","POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        # 首先获取到新闻分类，然后传递到模板页码，进行展示
        category_list = Category.query.all()
        categorys = []
        for category in category_list:
            categorys.append(category.to_dict())
        # 删除列表当中０的元素
        categorys.pop(0)
        data = {
            "categories":categorys
        }
        return render_template("news/user_news_release.html",data = data)
    # 获取到表单页码提交过来的数据，获取的是用户发布的新闻数据
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno = RET.PARAMERR,errmsg = "参数错误")

    user = g.user
    index_image = index_image.read()
    key = storage(index_image)
    # 用户发布完成之后，我们需要把当前发布的新闻存储到数据
    news = News()
    news.title = title
    news.source = "个人来源"
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    # 当前的状态１表示正在审核中
    news.status = 1
    db.session.add(news)
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "发布成功")






@profile_blue.route("/collection")
@user_login_data
def collection():
    # 当前表示用户所有收藏的新闻，获取所有新闻涉及到分页，那么肯定是从第一页开始
    page = request.args.get("p",1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    # 获取到当前登陆用户的所有的收藏新闻列表
    # 第一个参数表示页码
    # 第二个参数表示当前每个页码一共有多少条数据
    paginate = user.collection_news.paginate(page,10,False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    collections = []
    for item in  items:
        collections.append(item.to_dict())

    data = {
        "collections":collections,
        "current_page":current_page,
        "total_page":total_page,
    }

    return render_template("news/user_collection.html",data = data)




"""修改密码"""
@profile_blue.route("/pass_info",methods = ["GET","POST"])
@user_login_data
def pass_info():



    if request.method == "GET":
       return render_template("news/user_pass_info.html")

    user = g.user
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if not all([old_password,new_password]):
        return jsonify(errno = RET.PARAMERR,errmsg = "请输入密码")

    # 判断旧的密码是否正确，只有当旧密码正确，才能修改新的密码
    if not user.check_password(old_password):
        return jsonify(errno = RET.PARAMERR,errmsg = "旧密码错误")

    # 如果旧密码正确，那么直接更新到当前的数据库里面
    user.password = new_password
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "密码修改成功")




@profile_blue.route("/pic_info",methods= ["GET","POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":

        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_pic_info.html", data=data)
    avatar = request.files.get("avatar").read()
    # 如果上传成功,那么就会返回一个url地址,或者叫做key
    # 如果想在浏览器里面浏览刚刚 上传的图片,那么必须通过
    # 七牛的地址 + 刚刚返回的url
    # http: // oyucyko3w.bkt.clouddn.com / + url
    url = storage(avatar)

    user.avatar_url =  url
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "上传成功",data={"avatar_url": constants.QINIU_DOMIN_PREFIX + url})






"""修改个人信息"""
@profile_blue.route("/base_info",methods = ["GET","POST"])
@user_login_data
def base_info():
    user = g.user

    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_base_info.html",data = data)

    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")


    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    # 更新数据库
    db.session.commit()
    # 更新session里面的数据
    session["nick_name"] = user.nick_name

    return jsonify(errno = RET.OK,errmsg = "修改成功")




@profile_blue.route("/info")
@user_login_data
def info():
    user = g.user
    if not user:
        # 重新跳转到首页
        return redirect("/")
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("news/user.html",data = data)