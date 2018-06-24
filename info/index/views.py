import logging
from flask import render_template,current_app
from flask import request,jsonify
from flask import session

from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blue
"""
index.views:只放置首页的业务逻辑　　主要分析出前台给了我什么数据，《《我拿来怎么用》》，然后我需要返回什么数据给前台。。接口文档。。
"""
@index_blue.route("/news_list")
def news_list():
    # cid：首页上面的分类id，第二个参数是默认值
    cid = request.args.get("cid",1)

    # 页数，不传默认为第一页
    page = request.args.get("page", 1)
    # 每个页面有多少条数据，不传默认10条
    per_page = request.args.get("per_page","10")
    # 校验数据
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)

        # 3. 查询数据并分页
    filters = [News.status == 0]  # 0代表审核通过
    # TODO 如果分类cid不为1，那么添加分类id的过滤!!!!!!!!!
    if cid != 1:
        filters.append(News.category_id == cid)
    # 第一个参数表示当前是在哪个页面，page表示　　　　　　　第几页
    # 第二个参数表示当前页面一共有多少条数据  per_page  　 当前页面有多少条数据
    # # 第三个参数表示没有错误输出 1,2,3,4,5,6
    # if cid == 1:
    #    paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
    # else:
    # filter过滤器模糊查询 ，包含审核通过的所有新闻   paginate（词义：标页数，分页）   查询出的数据都需要转换成字典
    # 得到的paginate是一个对象，用这个对象来进行分页，分页也就用到两个参数而已，ｐａｇｅ，　ｐｅｒ——ｐａｇｅ
    # 通过断点可以看出执行到４4行已经取出了items中的十条数据，所以第４6行paginate.items是固定写法，就如同News.query
    # 下面这一行就已经计算出了总的数据条数，和分有多少页
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    # 每个页面上面需要展示的数据（以下是固定写法，看源码，用以下三个参数进行分页,上面已经算出了结果，下面只是取值而已）
    items = paginate.items
    # 当前页面
    current_page = paginate.page
    # 总页数
    total_page = paginate.pages

    news_list = []
    # 遍历出每个页面上需要展示的数据
    for news in items:
        news_list.append(news.to_dict())
    data = {
        # 表示当前页面需要展示的数据
        "news_dict_li":news_list,
        # 当前页（如第３页）
        "current_page":current_page,
        # 总页数
        "total_page":total_page,
        # 分类id
        "cid":cid
    }
    return jsonify(errno = RET.OK,errmsg = "ok",data = data)




@index_blue.route("/favicon.ico")
def xxxx():
    return current_app.send_static_file('news/favicon.ico')





# """主页"""
# @index_blue.route("/")
# def index():
#     user_id = session.get("user_id")
#     user = None
#     if user_id:
#        user =  User.query.get(user_id)
#     """
#     右边的热门新闻排序
#     """
#     news_model = News.query.order_by(News.clicks.desc()).limit(10)
#     print("*********************",news_model,"&&&&&&&&&&$$$$$$$$$$$&&&&&&&&&")
#     news_dict = []
#     for news in news_model:
#         news_dict.append(news.to_dict())
#     # print(news_dict)
#     """
#     最上面的分类数据
#     """
#     category_model = Category.query.all()
#     category_dict = []
#     for category in category_model:
#         category_dict.append(category.to_dict())
#     data = {
#         "user_info":user.to_dict() if user else None,
#         "click_news_list":news_dict,
#         "categories":category_dict
#     }
#     return render_template("news/index.html",data = data)


"""主页模块数据"""
@index_blue.route("/")
def index():
    user_id = session.get("user_id")   #session根据上下文取出存储的user信息
    user = None
    if user_id:
        user = User.query.get(user_id)  #表示用户存在

    """右边的热门新闻排序（查询点击量最高的数据）"""
    news_model = News.query.order_by(News.clicks.desc()).limit(10)  #根据新闻的点击量倒序排序，取出前十条数据
    news_dict = []  # 将十条完整的数据（新闻的各个字段）转化为字典存储于列表，因为前端需要接收json数据
    for news in news_model:
        news_dict.append(news.to_dict())

    """最上面的分类数据（查询分类数据表，然后展示出来）"""
    category_model = Category.query.all()   # all()以列表形式返回查询的所有结果
    category_dict = []
    for category in category_model:    #  遍历出查询到的所有分类
        category_dict.append(category.to_dict())   # 将遍历的数据转化为字典添加至列表
    data = {
        "user_info": user.to_dict() if user else None,
        # TODO 抽取的思路
        "click_news_list": news_dict,
        "categories": category_dict
    }
    return render_template("news/index.html", data = data)











