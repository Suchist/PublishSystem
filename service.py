#encoding:utf-8
from flask import Flask, render_template, request, redirect, url_for, jsonify,session,flash
from exts import db
from models import User,Article,Comment,Vote,Subject,VoteComment
import uuid,Check,os,config
from sqlalchemy import and_
from flask import Flask, current_app, url_for, make_response
from jinja2 import PackageLoader, Environment
import xhtml2pdf.pisa as pisa
from io import BytesIO
from werkzeug.utils import secure_filename
from action import validate_code


ALLOWED_EXTENSIONS = set(['pdf'])

from sqlalchemy import or_
app = Flask(__name__)
app.config.from_object(config)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024#限制上传文件大小为20M
db.init_app(app)


@app.route('/',methods=['GET','POST'])
def homePage():
    if request.method == 'GET':
        context = {
            'subjects': Subject.query.all()
        }
        #Article.query.order_by(create_time').all
        return render_template('HomePage.html', **context)
    else:
        subject_name = request.form.get('subject_name')
        subjectExist = Subject.query.filter(Subject.name == subject_name).first()
        if not subjectExist:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()
            return redirect(url_for('homePage'))
        else:
            return u'The subject already exist You can search it'

@app.route('/Subject/<subject_id>/')
def subjectDetail(subject_id):
    subject = Subject.query.filter(Subject.id == subject_id).first()
    return render_template("ArticleList.html",subject=subject)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/publish',methods=['GET','POST'])
def publish():
    if request.method == 'GET':
        return render_template('AuthorPage.html')
    else:
        id = str(uuid.uuid1())
        email = request.form.get('email')
        subject_name = request.form.get('article_subject')
        title = request.form.get('article_title')
        abstract = request.form.get('abstract')
        highlight = request.form.get('highlight')
        content = request.form.get('content')
        file = request.files['file']
        validate = request.form.get('validate')

        #check Email
        if Check.validateEmail(email) == 0:
            return u'You need enter correct email form'
        if subject_name==None:
            return u'You need enter subject name'
        if Check.inDictElement(subject_name):
            return u'Your subject should not include dirty words.'
        if title==None:
            return u'You need enter title'
        if Check.inDictElement(title):
            return u'Your title should not include dirty words.'
        if abstract==None:
            return u'You need enter abstract'
        if Check.inDictElement(abstract):
            return u'Your abstract should not include dirty words.'
        if  highlight==None:
            return u'You need enter highlight'
        if Check.inDictElement(highlight):
            return u'Your highlight should not include dirty words.'
        if  content==None:
            return u'You need enter content'
        if Check.inDictElement(content):
            return u'Your content should not include dirty words.'

        if session['code'] != validate:
            return u"The validate code is wrong please check"

        if file and allowed_file(file.filename):
            basepath = os.path.dirname(__file__)  # 当前文件所在路径
            upload_path = os.path.join(basepath, 'static\\uploads',
                                       secure_filename(file.filename))
            file.save(upload_path)
        else:
            return u"upload failed,The file format must be pdf"

        # hide email information

        user = User(id=id,email=email)
        article = Article(title=title, content=content, abstract=abstract, highlight=highlight,viewCount=0,likeNumber=0,unlikeNumber=0)
        article.author = user
        
        # check whether the article was published within a very short period.
        # 1.find the user according to the email
        # 2.check the title and createTime of the users.article
        userExist = User.query.filter(User.email == email).first()
        if userExist != None:
            if userExist.article.title == title and time.time()-userExist.article.createTime < 400:
                return 'You had published it within a very short period,please check it'

        #check whether the subject is exist
        subjectE = Subject.query.filter(Subject.name == subject_name).first()
        if subjectE==None:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()
            article.subject = subject
        else:
            article.subject = subjectE
            db.session.add(article)
            db.session.commit()
    return redirect(url_for('homePage'))


@app.route('/Article/<article_id>/')
def detail(article_id):
    article_detail=Article.query.filter(Article.id==article_id).first()
    article_detail.viewCount=article_detail.viewCount+1
    db.session.commit()
    return  render_template("Article.html",article=article_detail)

@app.route('/comment/',methods=['GET','POST'])
def addComment():
    user_id = str(uuid.uuid1())
    email = request.form.get('email')
    comment_content = request.form.get('comment')
    article_id = request.form.get('article_id')
    if Check.inDictElement(comment_content):
        return u'Your comments should not include dirty words.'

    user = User(id=user_id, email=Check.hiddenEmail(email))
    comment = Comment(content=comment_content )
    comment.author = user
    article = Article.query.filter(Article.id == article_id).first()
    comment.article = article

    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail',article_id=article_id))

@app.route('/search/')
def search():
    q=request.args.get('q')
    articles=Article.query.filter(or_(Article.title.contains(q),Article.content.contains(q))).order_by('createTime')
    return render_template('HomePage.html',articles=articles)


@app.route('/download/<articleId>', methods=['GET'])
def download_pdf(articleId):
    article = Article.findArticleById(articleId)
    env = Environment(loader=PackageLoader(current_app.name, 'templates'))
    template = env.get_template('article1.html') # 获得页面模板
    html = template.render(
        article=article).encode('utf-8')
    result = BytesIO()
    print(result)
    pdf = pisa.CreatePDF(BytesIO(html), result)
    print(pisa.CreatePDF(BytesIO(html), result))
    resp = make_response(result.getvalue())
    resp.headers["Content-Disposition"] = (
        "attachment; filename='{0}'; filename*=UTF-8''{0}".format(article.title+'.pdf'))
    resp.headers['Content-Type'] = 'application/pdf'
    return resp

@app.route('/isLikedById',methods=['GET', 'POST'])
def isLikedById():
    ip = request.remote_addr
    article_id = request.args.get("aid")
    voted = Vote.query.filter(and_(Vote.article_id == article_id, Vote.user_ip == ip)).all()
    if not voted:
        return jsonify(0), 200
    else:
        if voted[0].is_up == 1:
            print(voted[0].is_up)
            return jsonify(1), 200
        # 1 like #like变深
        else:
            #2 unlike颜色变深
            return jsonify(2), 200
# 点赞
@app.route('/upVote',methods=['GET', 'POST'])
def upVote():
    ip = request.remote_addr
    article_id = request.args.get("aid")
    voted = Vote.query.filter(and_(Vote.article_id == article_id, Vote.user_ip == ip)).all()
    article = Article.query.filter(Article.id==article_id).all()
    if not voted:
        vote = Vote(None,user_ip=ip, article_id=article_id, is_up=1)
        article[0].likeNumber = article[0].likeNumber + 1
        print(article[0].likeNumber)
        db.session.add(vote)
        db.session.commit()
        return jsonify(0), 200
    #没赞过返回0颜色变深
    else:
        return jsonify(1), 200
    #赞过了返回1颜色不变

# downvote
@app.route('/downVote',methods=['GET', 'POST'])
def downVote():
    ip = request.remote_addr
    article_id = request.args.get("aid")
    voted = Vote.query.filter(and_(Vote.article_id == article_id, Vote.user_ip == ip)).all
    article = Article.query.filter(Article.id == article_id).all
    result = []
    if not voted:
        vote = Vote(None,user_ip=ip, article_id=article_id, is_up=0)
        article[0].likeNumber = article[0].unlikeNumber + 1
        db.session.add(vote)
        db.session.commit()
        return jsonify(0), 200
    # 没有灭过返回0颜色变深
    else:
        #灭过了返回1颜色不变
        return jsonify(1), 200

@app.route('/code')
def get_code():
    image, code = validate_code()
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['code'] = code
    return response


# 点赞
@app.route('/upVoteComment',methods=['GET', 'POST'])
def upVoteComment():
    ip = request.remote_addr
    comment_id = request.args.get("cid")
    print(comment_id)
    comment_voted = VoteComment.query.filter(and_(VoteComment.comment_id == comment_id, VoteComment.user_ip == ip)).all()
    comment = Comment.query.filter(Comment.id==comment_id).all()
    if not comment_voted :
        votecomment = VoteComment(None,user_ip=ip, comment_id=comment_id, is_up=1)
        comment[0].likeNumber = comment[0].likeNumber + 1
        db.session.add(votecomment)
        db.session.commit()
        return jsonify(0), 200
    #没赞过返回0颜色变深
    else:
        return jsonify(1), 200
    #赞过了返回1颜色不变

# downvote
@app.route('/downVoteComment',methods=['GET', 'POST'])
def downVoteComment():
    ip = request.remote_addr
    comment_id = request.args.get("cid")
    comment_voted = VoteComment.query.filter(
        and_(VoteComment.id == comment_id, VoteComment.user_ip == ip)).all()
    comment = Comment.query.filter(Comment.id == comment_id).all()
    if not comment_voted:
        votecomment = VoteComment(None, user_ip=ip, comment_id=comment_id, is_up=0)
        comment[0].unlikeNumber = comment[0].unlikeNumber + 1
        db.session.add(votecomment)
        db.session.commit()
        return jsonify(0), 200
    # 没赞过返回0颜色变深
    else:
        return jsonify(1), 200
    # 赞过了返回1颜色不变



@app.route('/donation',methods=['GET','POST'])
def donate():
    return render_template('reward.html')

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80")
    )
