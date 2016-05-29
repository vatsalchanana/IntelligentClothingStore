
from django.conf.urls import url
from . import views
from django.conf.urls import include

urlpatterns = [
    # ex: /
    url(r'^$', views.product_list, name='product_list'),
    # ex: /review/5/
    url(r'^review/(?P<review_id>\w+)/$', views.review_detail, name='review_detail'),
   
    url(r'^product$', views.polls_list, name='polls_list'),
    
    url(r'^product/(?P<product_id>\w+)/$', views.product_detail, name='product_detail'),
    url(r'^product/(?P<product_id>\w+)/add_review/$', views.add_review, name='add_review'),
    # ex: /review/
    url(r'^review$',views.review_list,name = 'review_list'),
    url(r'^review/user/(?P<username>\w+)/$', views.user_review_list, name='user_review_list'),
    url(r'^review/user/$', views.user_review_list, name='user_review_list'),
    url(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),
    url(r'^image-search/', views.lists, name='lists'),
]