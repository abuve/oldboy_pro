#!/usr/bin/env python
#encoding=utf-8
from django.shortcuts import render,render_to_response, RequestContext

from django.http import HttpResponseRedirect, HttpResponse
from bbs.models import *
from django.contrib import comments 
# Create your views here.
import datetime,time
from django.contrib.auth.decorators import login_required 
from django.contrib import auth
import json

new_comment_dic ={}

def login(request):
	return render_to_response('login.html')
def logout(request):
	auth.logout(request)
	return HttpResponse("<h4>You've just logged out! <a href='/'>click here</a> to go back to main page</h4>")
def personal_info(request):
	return render_to_response("personal_info.html", {'login_user':request.user})

@login_required
def new_article(request):
	bbs_form = new_bbs_form() 
	return render_to_response('new_article.html', {'bbs_form':bbs_form})

def get_bbs_content(request,bbsid):
	obj = bbs.objects.get(id = int(bbsid))
	return HttpResponse(obj.content)

def get_data(request):
	print request.POST,'*****||||'
	dataType = request.POST['dataType']
	user_id = request.user.id
	print user_id
	return_list = []
	if dataType == 'msg':
		return_data = comments.Comment.objects.filter(web_user__user = user_id).order_by('-submit_date')[:50]
		for i in  return_data:
			return_list.append( (i.object_pk, i.comment, i.submit_date.strftime('%Y_%m_%d %H:%M:%S'),bbs.objects.get(id = i.object_pk).title)  )
	return HttpResponse(json.dumps(return_list) )

def add_new_article(request):
	web_user_name = web_user.objects.get(user__username=request.user)
	bbs_category,color,bbs_title = request.POST['category'], request.POST['color_type'], request.POST['bbs_title']
	
	content = request.POST['content']
	new_bbs_obj = bbs.objects.create(title = bbs_title, color_type= color, category = bbs_category, publish_date=datetime.datetime.now(), author = web_user_name, content = content )
	new_bbs_obj.save()

	return HttpResponseRedirect("/%s/" % request.POST['category'])
def upload_pic(request):
    if request.method == 'POST':
	print '========'
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            p = web_user.objects.get(user =  request.user.id)
            p.photo = form.cleaned_data['image']
            p.save()
            return HttpResponse('image upload success')
    return HttpResponse('allowed only via POST')



def account_login(request):
        username = request.POST['user']
        password = request.POST.get('password','')
        user = auth.authenticate(username=username,password=password)
        print user,'====='
	if user is not None: #and user.is_active:
                #correct password and user is marked "active"
                auth.login(request,user)
                return HttpResponseRedirect("/")
        else:
                return render_to_response('login.html',{'err':'Wrong username or password!'})

def index(request):

	return render_to_response('index.html',{'login_user': request.user})

def python_bbs(request):
	hot_bbs = bbs.objects.order_by('-comment_count')[:5]
	bbs_list = bbs.objects.filter(category= 'python').order_by('-publish_date')
	hot_comments = comments.Comment.objects.order_by('-submit_date')[:5]
	return render_to_response('blog.html', {'bbs_list': bbs_list,'login_user': request.user,'hot_list':hot_bbs,'hot_comments': hot_comments},context_instance=RequestContext(request))
def linux_bbs(request):
	hot_bbs = bbs.objects.order_by('-comment_count')[:5]
	hot_comments = comments.Comment.objects.order_by('-submit_date')[:5]
        bbs_list = bbs.objects.filter(category= 'linux').order_by('-publish_date')
	return render_to_response('blog.html', {'bbs_list': bbs_list,'login_user': request.user,'hot_list':hot_bbs,'hot_comments': hot_comments},context_instance=RequestContext(request))
def diary(request):
	hot_comments = comments.Comment.objects.order_by('-submit_date')[:5]
	hot_bbs = bbs.objects.order_by('-comment_count')[:5]
        bbs_list = bbs.objects.filter(category= 'diary').order_by('-publish_date')
	return render_to_response('blog.html', {'bbs_list': bbs_list,'login_user': request.user,'hot_list':hot_bbs,'hot_comments': hot_comments},context_instance=RequestContext(request))
def jobs(request):
        hot_comments = comments.Comment.objects.order_by('-submit_date')[:5]
        hot_bbs = bbs.objects.order_by('-comment_count')[:5]
        bbs_list = bbs.objects.filter(category= 'hiring').order_by('-publish_date')
        return render_to_response('blog.html', {'bbs_list': bbs_list,'login_user': request.user,'hot_list':hot_bbs,'hot_comments': hot_comments},context_instance=RequestContext(request))


def add_comment(request):
	print request.POST
	s=request.session
	parent_comment_id = ''
	if not request.user.is_authenticated(): # user not login yet
		print '\033[34;1m-----\033[0m',request.user ,request.user.id
		web_user_name = None 
		comment_user = None
		name,email,msg = request.POST['name'], request.POST['email'], request.POST['message']
	else:
		comment_user = request.user
		msg = request.POST['message']
		email, name = request.user.email, request.user.username
	        web_user_name = web_user.objects.get(user__username=request.user)
                print web_user_name.photo,'\033[34;1m--|||||---\033[0m'
	if request.POST.has_key('comment_id'):parent_comment_id = request.POST['comment_id']  #this comment is a child comment 
	bbs_id = request.POST['bbs_id']
	print new_comment_dic

	if new_comment_dic.has_key(s._session_key):
		time_diff = time.time() - new_comment_dic[ s._session_key ]
		if time_diff >30:
			a=comments.models.Comment.objects.create(content_type_id = 9, object_pk=bbs_id, ip_address= parent_comment_id,user=comment_user, web_user = web_user_name,  site_id=1, user_name=name,user_email=email, comment= msg ,submit_date=datetime.datetime.now())
			a.save()
	                new_comment_dic[s._session_key]  = time.time() #add a new comment mark or renew the time stamp  
		else:
			print "need to send a comment after %s seconds" % time_diff
                        return HttpResponse("need to send a comment after %s seconds" % time_diff)
	else:  #first time submit the comment
		new_comment_dic[s._session_key]  = time.time() #add a new comment mark or renew the time stamp  
		a=comments.models.Comment.objects.create(content_type_id = 9, object_pk=bbs_id, ip_address= parent_comment_id,  site_id=1,user=comment_user, web_user=web_user_name, user_name=name,user_email=email, comment= msg ,submit_date=datetime.datetime.now())
		a.save()

	bbs_obj = bbs.objects.get(id = bbs_id)
	bbs_comments = comments.models.Comment.objects.filter(object_pk= bbs_id)
	return render_to_response('bbs_detail.html', {'bbs_obj':bbs_obj, 'bbs_comments': bbs_comments,'login_user': request.user})

def add_agree(request):
	bbs_id = request.POST['bbs_id']
	bbs_obj = bbs.objects.get(id = bbs_id)
	if request.POST['agree'] == 'YES':
		bbs_obj.agree_count += 1
	else:
		bbs_obj.agree_count -= 1
	bbs_obj.save()
	print bbs_id,'||||'
	return HttpResponse( bbs_obj.agree_count )
def bbs_detail(request):
	print len(request.POST),request.POST
	
	if len(request.POST) != 0:
		bbs_id =  request.POST['BBS_ID'].split('_')[1]
		bbs_obj = bbs.objects.get(id = bbs_id)
		bbs_comments = comments.models.Comment.objects.filter(object_pk= bbs_id)
		print bbs_comments
		bbs_obj.view_count += 1
		bbs_obj.save()
		return render_to_response('bbs_detail.html', {'bbs_obj':bbs_obj, 'bbs_comments': bbs_comments, 'login_user': request.user})
	else:
		bbs_list = bbs.objects.all()
		return render_to_response('blog.html', {'bbs_list': bbs_list})

@login_required
def sign_in_page(request):
	user_id = request.user.id
	username = request.user
	current_time = time.strftime('%H:%M')
	current_date = datetime.date.today()
	
	check_class_date = class_course.objects.filter(date = current_date).values('start_time','end_time')
	class_name_id = class_course.objects.filter(date = current_date).values('class_name')
	class_name_info = class_list.objects.filter(id = class_name_id).values('name')
        if request.is_ajax():
		# Sign in Post action Start.
		# Check today class status.
		if len(check_class_date) ==0:
			# None of class today, End user request.
			return HttpResponse('对不起，今天没有课程，无法签到！')
		else:
			# Judge user in class.
			user_list_data = class_list.objects.filter(name = class_name_info).values("user")
			user_list = []
			for user_id_list in user_list_data:
				user_list.append(str(user_id_list['user']))
			if str(user_id) not in user_list:
				return HttpResponse('对不起，今天的课程不属于您，如有疑问请及时联系老师！')
			else:
				# Judge user signIn status.
				user_signIn_stat = sign_in.objects.filter(sign_time__startswith = current_date).filter(user_id = user_id)
				if len(user_signIn_stat) == 1:
					return HttpResponse('您今天已经签到，请不要重复提交，谢谢！')
				else:
					# Judge class sign allow time.
					d1 = datetime.datetime.now()
					for allow_times in check_class_date:
						# Define allow signIn time.
						allow_time_signIn = allow_times['start_time'] + datetime.timedelta(hours=-2)
						# Define allow signOut time.
						allow_time_signOut = allow_times['end_time']
					# Start user signIn allow times check.
					if d1 < allow_time_signIn:
						return HttpResponse('还没到点哦，今天开始签到的时间是 %s' %allow_time_signIn.strftime('%H:%M'))
					elif d1 > allow_time_signOut:
						return HttpResponse('不能签到了，今天%s就已经下课啦，如有疑问请及时联系老师！' %allow_time_signOut.strftime('%H:%M'))
					# End user signIn allow times check.
					else:
						# Define signIn status, 
						sign_stat = None
						# Judge sign in stat.
						#current_date_check = d1.strftime('%Y-%m-%d %H:%M')
						#current_date_record = d1.strptime(current_date_check,'%Y-%m-%d %H:%M')
						current_time = d1
						class_start_time = allow_times['start_time']
						if current_time > class_start_time:
							sign_stat = "迟到"
						else:
							sign_stat = "正常"
						# Get foreign key instance.
						user_id_instance = web_user.objects.get(user_id = user_id)
						class_name_instance = class_list.objects.get(name = class_name_info)
						# Update user sign data.
						sign_in_data = sign_in.objects.create(
								user = user_id_instance,
								sign_time = current_time,
								class_name = class_name_instance,
								status = sign_stat)
						sign_in_data.save()
						return HttpResponse('签到成功')
		# Sign in Post action End.
	else:
		# Check today class status.
		if len(check_class_date) ==0:
			return render_to_response('sign_in.html',{'login_user':request.user,'class_user_signIn_yes':0,'class_user_signIn_no':1})
		else:
			class_user_total = len(class_list.objects.filter(name = class_name_info).values("user"))
			class_user_signIn_yes = len(sign_in.objects.filter(sign_time__startswith = datetime.date.today()))
			class_user_signIn_no = class_user_total - class_user_signIn_yes
			return render_to_response('sign_in.html',{'login_user':request.user,'class_user_signIn_yes':class_user_signIn_yes,'class_user_signIn_no':class_user_signIn_no})


@login_required
def sign_in_list(request):
	username = request.user
	sign_in_data = sign_in.objects.filter(user = request.user.id)
	print sign_in_data
	return render_to_response('sign_in_list.html',{'login_user':request.user,'sign_in_data':sign_in_data})
