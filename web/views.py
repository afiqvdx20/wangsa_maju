from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.http import Http404
from .models import Car,Myrating
from django.contrib import messages
from .forms import UserForm
from django.db.models import Case, When
from .recommendation import Myrecommend
import numpy as np
import pandas as pd


# for recommendation
def recommend(request):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	df=pd.DataFrame(list(Myrating.objects.all().values()))
	nu=df.user_id.unique().shape[0]
	current_user_id= request.user.id
	# if new user not rated any car
	if current_user_id>nu:
		car=Car.objects.get(id=15)
		q=Myrating(user=request.user,car=car,rating=0)
		q.save()

	print("Current user id: ",current_user_id)
	prediction_matrix,Ymean = Myrecommend()
	my_predictions = prediction_matrix[:,current_user_id-1]+Ymean.flatten()
	pred_idxs_sorted = np.argsort(my_predictions)
	pred_idxs_sorted[:] = pred_idxs_sorted[::-1]
	pred_idxs_sorted=pred_idxs_sorted+1
	print(pred_idxs_sorted)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pred_idxs_sorted)])
	car_list=list(Car.objects.filter(id__in = pred_idxs_sorted,).order_by(preserved)[:10])
	return render(request,'web/recommend.html',{'car_list':car_list})


# List view
def index(request):
	cars = Car.objects.all()
	query  = request.GET.get('q')
	if query:
		cars = Car.objects.filter(Q(title__icontains=query)).distinct()
		return render(request,'web/list.html',{'cars':cars})
	return render(request,'web/list.html',{'cars':cars})


# detail view
def detail(request,car_id):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	cars = get_object_or_404(Car,id=car_id)
	#for rating
	if request.method == "POST":
		rate = request.POST['rating']
		ratingObject = Myrating()
		ratingObject.user   = request.user
		ratingObject.car  = cars
		ratingObject.rating = rate
		ratingObject.save()
		messages.success(request,"Your Rating is submited ")
		return redirect("index")
	return render(request,'web/detail.html',{'cars':cars})


# Register user
def signUp(request):
	form =UserForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
	context ={
		'form':form
	}
	return render(request,'web/signUp.html',context)


# Login User
def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
			else:
				return render(request,'web/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'web/login.html',{'error_message': 'Invalid Login'})
	return render(request,'web/login.html')

#Logout user
def Logout(request):
	logout(request)
	return redirect("login")
