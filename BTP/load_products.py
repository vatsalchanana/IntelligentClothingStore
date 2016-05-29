import sys, os 
import pandas as pd
import gzip


sys.path.insert(0, '/Users/vatsalchanana/Desktop/BTP/BTP/tensorflow/tensorflow/models/image/imagenet/')

import classify_image

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BTP.settings")

import django
django.setup()

from recommender.models import Product

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



def save_Product_from_row(Product_row):
    product = Product()
    product.asin = Product_row['asin']
    product.name = Product_row['title']
    product.imURL = Product_row['imUrl']
    product_image = "/Users/vatsalchanana/Desktop/BTP/BTP/Images/"+  Product_row['asin']+".jpg"
    
    deep_f,label=classify_image.get_features_and_label(product_image)
    product.keyword=label
    deep_f_v2 = []
    for i in deep_f:
        deep_f_v2.append(i)
    
    deep_f_string = ""
    for i in deep_f_v2:
        deep_f_string += str(i) + " "
        
    product.features = deep_f_string
    if isinstance(product.name,str) :
        print product.name + product.asin 
        product.save()

    
    
if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])
        product_df = getDF(sys.argv[1])
        print product_df['title']

        product_df.apply(
            save_Product_from_row,
            axis=1
        )
        gl=0;
        print "There are {} products".format(Product.objects.count())
        
    else:
        print "Please, provide product file path"