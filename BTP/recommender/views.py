
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Create your views here.
from .models import Review,Product,Cluster,Document
from .forms import ReviewForm,DocumentForm
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .suggestions import update_clusters
from django_pandas.io import read_frame
from .forms import PollsForm
import math
import graphlab
import sklearn
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sklearn.neighbors import DistanceMetric
from sklearn.neighbors.ball_tree import BallTree
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import sys, os 
sys.path.insert(0, '/Users/vatsalchanana/Desktop/BTP/BTP/tensorflow/tensorflow/models/image/imagenet/')
import classify_image

def review_list(request):
	review_list = Review.objects.order_by('-pub_date')[:9]
	context = {'review_list':review_list}
	return render(request,'recommender/review_list.html',context)

def review_detail(request,review_id):
	review=get_object_or_404(Review, pk=review_id)
	return render(request,'recommender/review_detail.html',{'review':review})

def product_list(request):
	product_list = sorted(
		list(Product.objects.all()), 
		key=lambda x: x.num_reviews(), 
		reverse=True
		)
	context = {'product_list':product_list}
	return render(request,'recommender/product_list.html',context)
	
def product_detail(request,product_id):
	product = get_object_or_404(Product, asin =product_id)
	review_list = Review.objects.filter(product = product)[:9]
	form = ReviewForm()
	recommended_products = similar_products(product)
	return render(request,'recommender/product_detail.html',{'product':product,'form':form,'review_list':review_list,'product_list':recommended_products})

@login_required
def add_review(request, product_id):
	product = get_object_or_404(Product, asin = product_id)
	form = ReviewForm(request.POST)
	if form.is_valid():
		rating = form.cleaned_data['rating']
		comment = form.cleaned_data['review_text']
		user_name = request.user.username
		review = Review()
		review.product = product
		review.user_name = user_name
		review.reviewer_id = user_name
		
		review.rating = rating
		review.review_text = comment
		review.pub_date = datetime.datetime.now()
		review.save()
		update_clusters()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse('recommender:product_detail', args=(product.asin,)))

	return render(request, 'recommender/product_detail.html', {'product': product, 'form': form})

def user_review_list(request, username=None):
	if not username:
		username = request.user.username
	review_list = Review.objects.filter(user_name = username).order_by('-pub_date')
	reviewer_id = username
	
	if review_list:
		reviewer_id = review_list[0].reviewer_id
	
		
	context = {'review_list' :review_list, 'username' : username,'reviewer_id':reviewer_id}
	return render(request,'recommender/user_review_list.html',context)

@login_required
def user_recommendation_list(request):
	user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('product')
	user_reviews_product_ids = set(map(lambda x: x.product.asin, user_reviews))
	try:
		user_cluster_name = \
			User.objects.get(username=request.user.username).cluster_set.first().name
	except: # if no cluster has been assigned for a user, update clusters
		update_clusters()
		user_cluster_name = \
			User.objects.get(username=request.user.username).cluster_set.first().name
	# get usernames for other members of the cluster
	user_cluster_other_members = \
		Cluster.objects.get(name=user_cluster_name).users \
			.exclude(username=request.user.username).all()
	other_members_usernames = set(map(lambda x: x.username, user_cluster_other_members))

   
	other_users_reviews = \
		Review.objects.filter(user_name__in=other_members_usernames) \
			.exclude(product__asin__in=user_reviews_product_ids)
	other_users_reviews_product_ids = set(map(lambda x: x.product.asin, other_users_reviews))

	
	product_list = sorted(
		list(Product.objects.filter(asin__in=other_users_reviews_product_ids)), 
		key=lambda x: x.average_rating, 
		reverse=True
	)
	new_product_list = product_list[:10]
	similar_prod_list=[]
	for i in new_product_list:
		si = similar_products(i)
		for j in si:
			similar_prod_list.append(j)
	final_list = similar_prod_list + new_product_list
	
	user_product_list = list(Product.objects.filter(asin__in = user_reviews_product_ids))
	similar_user_list = []
	for i in user_product_list:
		usi = similar_products(i)
		for j in usi:
			if j not in user_product_list:
				similar_user_list.append(j)

	
	return render(request,'recommender/user_recommendation_list.html',{'username':request.user.username,'product_list':final_list,'similar_product_list':similar_user_list})

def polls_list(request):
	form=PollsForm(request.GET or None)
	if form.is_valid():
		queryset=Product.objects.all()
		myarray = list()
		for index in range(len(queryset)):
			keyword_list = queryset[index].keyword
			keyword_list = keyword_list.replace(" ", "")
			keyword_list = keyword_list.split(',')
			name_list = queryset[index].name
			name_list = name_list.split()
			query_list = form.cleaned_data["name"].split()
			total_score = 0
			for word in query_list:
				score = 1000000000
				for kw in keyword_list:
					score = min(score, editD(kw, word))
				for nam in name_list:
					score = min(score, editD(nam, word))
				total_score = total_score + score
			myarray.append((total_score, index))
		myarray.sort()  
		
		resultset = list()
		for index in range(int(len(myarray)*0.05)):
			resultset.append(queryset[myarray[index][1]])
		query_ascii =""
		for word in query_list:
			query_ascii+=(" "+word.encode("ascii"))
		context={
			"product_list":resultset,
			"query":query_ascii
		}
		return render(request,"recommender/search_products.html",context)
	context= {
	"form":form,
	}
	return render(request,"recommender/polls_form.html",context)
	
def editD(s1, s2):
	if len(s1) > len(s2):
		s1, s2 = s2, s1
	distances = range(len(s1) + 1)
	for i2, c2 in enumerate(s2):
		distances_ = [i2+1]
		for i1, c1 in enumerate(s1):
			if c1 == c2:
				distances_.append(distances[i1])
			else:
				distances_.append(0 + min((100 + distances[i1], 1 + distances[i1 + 1], 1+distances_[-1])))
		distances = distances_
	return distances[-1]

def similar_products(product):
	qs = Product.objects.all()
	df=read_frame(qs)
	df['idx'] = range(1, len(df) + 1)
	feature_list=[]
	asin_list=[]
	product_index = 0
	inn=0
	for prod in qs:
		feature_list.append(prod.get_features())
		asin_list.append(prod.asin)
		if prod.asin == product.asin:
			product_index = inn
		inn+=1
		
	nparray = np.asarray(feature_list)
	#print nparray
	tree = BallTree(nparray)              
	dist, ind = tree.query(nparray[product_index], k=5)
	print ind
	index = ind[0]
	recom = index[1:]
	recommended_asins =[];
	
	for i in recom:
		recommended_asins.append(asin_list[i])
	recommended_prods = Product.objects.filter(asin__in = recommended_asins)
	return recommended_prods

def lists(request):
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = Document(docfile = request.FILES['docfile'])
			newdoc.save()
			documents = Document.objects.all()
			
			# Redirect to the document list after POST

			
			product_image = "/Users/vatsalchanana/Documents/Image_exper/BTP/BTP"+  newdoc.docfile.url
			
			deep_f,label=classify_image.get_features_and_label(product_image)
			
			deep_f_v2 = []
			for i in deep_f:
				deep_f_v2.append(i)
			
			deep_f_string = ""
			for i in deep_f_v2:
				deep_f_string += str(i) + " "
				
			deep_f_np = np.asarray(deep_f_v2)
			similar_prods = similar_products2(deep_f_np)
			print product_image
			print label
			print deep_f_string
			print deep_f
			print "Done"
			
			return render(request,"recommender/list.html",{'document': newdoc,'product_list':similar_prods})
	else:
		form = DocumentForm()
	documents = Document.objects.all()
	print documents[len(documents)-1].docfile.url
	return render_to_response('recommender/image-search.html',{'documents': documents, 'form':form},context_instance = RequestContext(request))


def similar_products2(deep_f):
	qs = Product.objects.all()
	df=read_frame(qs)
	df['idx'] = range(1, len(df) + 1)
	feature_list=[]
	asin_list=[]

	for prod in qs:
		feature_list.append(prod.get_features())
		asin_list.append(prod.asin)
	
		
	nparray = np.asarray(feature_list)
	#print nparray
	tree = BallTree(nparray)              
	dist, ind = tree.query(deep_f, k=5)
	print ind
	index = ind[0]
	recom = index[0:]
	recommended_asins =[];
	
	for i in recom:
		recommended_asins.append(asin_list[i])
	recommended_prods = Product.objects.filter(asin__in = recommended_asins)
	return recommended_prods

#    image_train = graphlab.SFrame(data=df)
#    cur_prod = image_train[18:19]
#    print cur_prod
#    print image_train
#    knn_model = graphlab.nearest_neighbors.create(image_train, features = ['features'],label = 'asin',distance = 'levenshtein',method = 'ball_tree')
#    knn_model.save('my_knn')
#    #knn_model= graphlab.load_model('my_knn')
#    #print knn_model.query(cur_prod)
#    #knn_model = graphlab.nearest_neighbors.create(image_train, features = ['features'],label = 'keywords')