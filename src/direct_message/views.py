from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render_to_response, RequestContext, Http404, HttpResponseRedirect, render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from django.contrib.sites.models import Site
from products.forms import ProductForm
from courses.forms import CourseForm
from courses.models import Course
from .models import DirectMessage, Convo
from .forms import ComposeForm
from accounts.models import MyUser
from local.models import Place
import hashlib, datetime, random
from django.utils import timezone
from accounts.models import University
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

import json

def messaging_all(request, id,profid):
	if request.user.is_authenticated():
		try:
			user = MyUser.objects.get(id=profid)
			school = University.objects.get(id=id)
		except:
			uni = request.user.university.id
			user_id = request.user.id
			return HttpResponseRedirect(reverse('messaging_all', args=(uni,user_id)))

		if user.id == request.user.id and school.id == request.user.university.id:
			convos = Convo.objects.filter(primary_user=request.user)

			received_messages = DirectMessage.objects.filter(receiver=request.user)
			sent_messages = DirectMessage.objects.filter(sender=request.user)

			sender_list = []
			id_list = []

			for item in sent_messages:
					#check if convo's secondary_user is the receiver user in queryset convos.If true add to lists
					for convo in convos:
						if not item.receiver.id in id_list:
							if convo.secondary_user.id == item.receiver.id:
								sender_list.append(item.receiver.first_name +" "+ item.receiver.last_name)
								id_list.append(item.receiver.id)
						

			for item in received_messages:
				#check if convo's secondary_user is the sender user in queryset convos.If true add to lists
				for convo in convos:
					if not item.sender.id in id_list:
						if convo.secondary_user.id == item.sender.id:
							sender_list.append(item.sender.first_name +" "+ item.sender.last_name)
							id_list.append(item.sender.id)

			send_id_list = zip(sender_list, id_list)
			if not send_id_list:
				return render_to_response('messages/message-all.html', locals(), context_instance=RequestContext(request))
				
			else:
				first = send_id_list[0]
				return HttpResponseRedirect(reverse('messaging', args=(request.user.university.id,first[1])))

		else:
			uni = request.user.university.id
			userid = request.user.id
			return HttpResponseRedirect(reverse('messaging_all', args=(uni,userid)))

	else:
		return HttpResponseRedirect('/login/')

	

def messaging(request, id, profid):
	if request.user.is_authenticated():
		try:
			#checking if the id in message/thread/id is actually a user and school id is a school
			user = MyUser.objects.get(id=profid)
			school = University.objects.get(id=id)
		except:
			#if not then redirect them 
			#if the request.user has either sent a message or received a message take them to to the first item.
			received_messages = DirectMessage.objects.filter(receiver=request.user)
			sent_messages = DirectMessage.objects.filter(sender=request.user)
			sender_list = []
			id_list = []
			for item in sent_messages:
				if not item.receiver.id in id_list:
					sender_list.append(item.receiver.first_name +" "+ item.receiver.last_name)
					id_list.append(item.receiver.id)

			for item in received_messages:
				if not item.sender.id in id_list:
					sender_list.append(item.sender.first_name +" "+ item.sender.last_name)
					id_list.append(item.sender.id)
			send_id_list = zip(sender_list, id_list)
			try:
				first = send_id_list[0]
				return HttpResponseRedirect(reverse('messaging', args=(request.user.university.id,first[1])))
			except:
				# if no sent or received messages then redirect to message/all/id blank.
				uni = request.user.university.id
				userid = request.user.id
				return HttpResponseRedirect(reverse('messaging_all', args=(uni,userid)))

		
		# if able to find the user with the id, and request.user.id is not user.id 

		if not request.user.id == user.id:
			if request.user.university == school and user.university == school:
				#then get what ever the request.user received or sent for messages
				to_convo = DirectMessage.objects.filter(receiver=request.user).filter(sender=user)
				from_convo = DirectMessage.objects.filter(receiver=user).filter(sender=request.user)
				#filter all convos whose primary user is the request.user
				#checking to see if user has not deleted conversation
				convos = Convo.objects.filter(primary_user=request.user)

				time_list = []
				message_list = []
				receiver_list = []
				send_list = []

				for item in to_convo:
					for convo in convos:
						#check if convo's secondary_user is the sender user in queryset convos.If true add to lists
						if convo.secondary_user.id == item.sender.id:
							if item.timestamp >= convo.timestamp:
								time_list.append(item.timestamp)
								message_list.append(item.body)
								receiver_list.append('You')
								send_list.append(item.sender.first_name +" "+ item.sender.last_name)

				for item in from_convo:
					for convo in convos:
						#check if convo's secondary_user is the receiver user in queryset convos.If true add to lists
						if convo.secondary_user.id == item.receiver.id:
							if item.timestamp >= convo.timestamp:
								time_list.append(item.timestamp)
								message_list.append(item.body)
								receiver_list.append(item.receiver.first_name +" "+ item.receiver.last_name)
								send_list.append('You')

				g = zip(time_list, message_list, receiver_list, send_list )
				message_convo = sorted(g, key=lambda x: x[0])
				unread = DirectMessage.objects.filter(receiver=request.user).filter(read=False)
				convos = Convo.objects.filter(primary_user=request.user)
				count_in_convos = []
				if unread:
					for item in unread:
						for convo in convos:
							if convo.secondary_user.id == item.sender.id:
								count_in_convos.append(item)
					count = len(count_in_convos)
				else: 
					count = 0
				for item in unread:
					if item.sender == user:
						item.read = True
						item.save()

				convos = Convo.objects.filter(primary_user=request.user)
				received_messages = DirectMessage.objects.filter(receiver=request.user)
				sent_messages = DirectMessage.objects.filter(sender=request.user)
				sender_list = []
				id_list = []
				count_list = []
				for item in sent_messages:
					#check if convo's secondary_user is the receiver user in queryset convos.If true add to lists
					for convo in convos:
						if not item.receiver.id in id_list:
							if convo.secondary_user.id == item.receiver.id:
								sender_list.append(item.receiver.first_name +" "+ item.receiver.last_name)
								id_list.append(item.receiver.id)
						

				for item in received_messages:
					#check if convo's secondary_user is the sender user in queryset convos.If true add to lists
					for convo in convos:
						if not item.sender.id in id_list:
							if convo.secondary_user.id == item.sender.id:
								sender_list.append(item.sender.first_name +" "+ item.sender.last_name)
								id_list.append(item.sender.id)
						
						
				send_id_list = zip(sender_list, id_list)

				
				
				return render_to_response('messages/message-thread.html', locals(), context_instance=RequestContext(request))
			else:
				uni = request.user.university.id
				userid = request.user.id
				return HttpResponseRedirect(reverse('messaging_all', args=(uni,userid)))
		
		else:
			uni = request.user.university.id
			userid = request.user.id
			return HttpResponseRedirect(reverse('messaging_all', args=(uni,userid)))
	else:
		return HttpResponseRedirect('/login/')



def delete_message(request, id, profid):

	try:

		user = MyUser.objects.get(id=profid)
		school = University.objects.get(id=id)
	except:
		return HttpResponseRedirect(reverse('messaging_all', args=(request.user.university.id,)))
	
	try:
		convos = Convo.objects.get(primary_user=request.user, secondary_user=user)
		convos.delete()
		response_data = {}
		
		new_data = json.dumps(response_data)

		return HttpResponse(new_data, content_type='application/json')
	except:

		return HttpResponseRedirect(reverse('messaging_all', args=(request.user.university.id,)))





				
def inbox(request):
	places = Place.objects.all()
	courses = Course.objects.filter(user=request.user)
	course_form = CourseForm(request.POST or None, request.FILES or None, prefix='course')
	product_form = ProductForm(request.POST or None, request.FILES or None, prefix='product')
	messages = DirectMessage.objects.filter(receiver=request.user)
	compose_form = ComposeForm(request.POST or None, request.FILES or None, prefix='message')

	sender_list = []
	id_list = []
	for item in messages:
		if not item.sender.first_name +" "+ item.sender.last_name in sender_list:
			sender_list.append(item.sender.first_name +" "+ item.sender.last_name)
			id_list.append(item.sender.id)
	send_id_list = zip(sender_list, id_list)






	
	return render_to_response('messages/inbox.html', locals(), context_instance=RequestContext(request))



def message(request):
    
  
    if request.method == "POST":
        user_form = ComposeForm(request.POST or None)
        user_id = request.POST.get('id')
        user=MyUser.objects.get(id=user_id)
        if user_form.is_valid():
			try:
				obj1 = Convo.objects.get(primary_user=request.user, secondary_user=user)

			except Convo.DoesNotExist:
				convo1 = Convo(primary_user=request.user, secondary_user=user)
				convo1.save()
				
			try:
				obj2 = Convo.objects.get(primary_user=user, secondary_user=request.user)
			except Convo.DoesNotExist:
				convo2 = Convo(primary_user=user, secondary_user=request.user)
				convo2.save()

			site = request.META['HTTP_HOST']
			body = user_form.cleaned_data['body']
			send_message = user_form.save(commit=False)
			send_message.sender = request.user
			send_message.receiver = user

			send_message.body = body
			send_message.sent = datetime.datetime.now()
			send_message.save()
			email_subject = 'New message on Student Grounds!'
			email_body = "Hey %s %s, you got a new message from %s %s! Check it out: %s" % (user.first_name, user.last_name, send_message.sender.first_name, send_message.sender.last_name, site )


			send_mail(email_subject, email_body, 'info@studentgrounds.org',
			    [user.email], fail_silently=False)


			response_data = {}
			response_data['body'] = send_message.body.replace("\\n", "\\\\n")
			response_data['sent'] = timezone.localtime(send_message.sent).strftime('%b. %d, %Y, %-I:%M %-P')
			response_data['user_id'] = user.id
			new_data = json.dumps(response_data)

			return HttpResponse(new_data, content_type='application/json')