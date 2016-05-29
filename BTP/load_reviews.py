import sys, os 
import pandas as pd
import gzip
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BTP.settings")

import django
django.setup()

from recommender.models import Product,Review

from django.contrib.auth.models import User

def parse(path):
    g = gzip.open(path, 'rb')
    for l in g:
      yield eval(l)

def getDF(path):
    i = 0
    df = {}
    for d in parse(path):
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient='index')



def save_review_from_row(review_row):
    review = Review()
    review.id = review_row['id']
    review.pub_date = datetime.datetime.strptime(review_row['reviewTime'],"%m %d, %Y")
    review.reviewer_id = review_row['reviewerName']
    review.user_name = review_row['reviewerID']
    review.rating = review_row['overall']
    review.review_text = review_row['reviewText']
    num_results = Product.objects.filter(asin = review_row['asin']).count()
    if(num_results == 1):
        review.product = Product.objects.get(asin = review_row['asin'])
        print review.id
        review.save()
        user = User()
        user.username = review_row['reviewerID']
        num_res = User.objects.filter(username = review_row['reviewerID']).count()
        if(num_res ==0):
            print user
            user.save()
    
if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])
        review_df = getDF(sys.argv[1])
        review_df['id'] = review_df.index

        review_df.apply(
            save_review_from_row,
            axis=1
        )
        
        print "There are {} reviews in DB".format(Review.objects.count())
        
    else:
        print "Please, provide Reviews file path"