from django.contrib import admin

# Register your models here.

from models import Product, Review, Cluster

class RecommenderAdmin(admin.ModelAdmin):
    model = Review
    list_display = ('product','rating','user_name','review_text')
    list_filter = ['product','user_name']
    search_fields = ['comment']

class ClusterAdmin(admin.ModelAdmin):
    model = Cluster
    list_display = ['name', 'get_members']
    
admin.site.register(Product)
admin.site.register(Review, RecommenderAdmin)
admin.site.register(Cluster, ClusterAdmin)