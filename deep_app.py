from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="loginfo.log", level=logging.INFO)


from pymongo.mongo_client import MongoClient     # For Mongodb 
from pymongo.server_api import ServerApi

uri = "mongodb+srv://Deep:<password>@cluster0.fzpbpri.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            website_url = "https://www.snapdeal.com/search?keyword="+searchString
            uClient = uReq(website_url)
            snapdealPage = uClient.read()
            uClient.close()
            snapdeal_html = bs(snapdealPage)
            bigbox = snapdeal_html.findAll("section",{"data-dpidt":"pdt_grd"})

            # filename = searchString + ".csv"
            # fw = open(filename, "w")
            # headers = "URL, Response Status, Product Highlight\n"
            # fw.write(headers)

            reviews = []
           

            for i in bigbox:
                productlink = i.div.a['href']
                url = productlink
                print(productlink)
                
                product_req = requests.get(productlink)
                if str(product_req) == '<Response [200]>':
                    resp_status = 'success'
                product_req.encoding = 'utf-8'
                print(product_req)
                
                product_html = bs(product_req.text)
                # print(product_html)
                
                box = product_html.find("section",{"class":"product-specs"})
                highlight = box.div.find("div",{"class":"tab-container"}).div.div.find("div",{"class":"spec-body p-keyfeatures"}).findAll("span",{"class","h-content"})

                highl_str = ""
                for k in highlight:
                    highl_str = highl_str + str(k.text) + "\n"
                    logging.info(f"This is higlight {highl_str}")
                
                mydict = {"URL": url, "Response_Status" : resp_status, "Highlight" : highl_str}
                reviews.append(mydict)

            # Creating a database
            db = client['Discription']  
            coll = db['highlight']      # Creating collections. 
            coll.insert_many(reviews)   # Inserting reviews to database.

            return render_template('result.html', reviews=reviews[0:])
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    
    else:
        return render_template('index.html')
            

if __name__=="__main__":
    app.run(host="0.0.0.0")
