# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 14:59:34 2020

@author: USER
"""
from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, abort
import time
import os
import base64
from PIL import Image
from demo_test import transfer
from flask_cors import CORS
from datetime import datetime
from imgurpython import ImgurClient
import cv2


app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])

def return_img_stream(img_origin):
  img_base64 = ''
  with open(img_origin, 'rb') as file:
    img_base64 = base64.b64encode(file.read())
    img_base64 = img_base64.decode('utf-8')
 
  return img_base64

def upload_photo(image_url):
    client_id = '44ece24e9fd2d66'
    client_secret = '555a538a8c0d1f1e57afc03cb68679e62f33ffed'
    access_token = 'c22e21dd71b0da8d356e016b94399a359e1e2606'
    refresh_token = '14d0098a4f9dcf3b493593df1ee2351fae041e23'
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    album = None # You can also enter an album ID here
    config = {
      'album': album,
    }

    print("Uploading image... ")
    image = client.upload_from_path(image_url, config=config, anon=False)
    print("Done")    
    return image['link']

@app.route('/upload')
def upload_test():
    return render_template('flask_up.html')

 
@app.route('/up_photo', methods=['post'])
def up_photo():
    img = request.files['photo']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
    img.save(img_path)
    style_img = '.jpg'
    result = transfer(style_img, img_path)
    result_img = return_img_stream(result)
    return render_template('show_img.html', result_img = result)

@app.route("/api", methods=["GET"])
def get():
    return jsonify(hello = 'Yusha!' , user= 'Me')

@app.route("/api", methods=["post"])
def post_js():
    spent_time = datetime.now()
    request_data = request.get_json()
    img_data = request_data['fetch_img_64']
    choice_ = request_data['user_choice']
    style = request_data['style_img']
    print(img_data)
    img_data = base64.b64decode(img_data)  # 解碼
    filename = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    filename += 'pic.jpg'
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename )
    with open(img_path, 'wb') as file:
      file.write(img_data)  # 將解碼得到的資料寫入到圖片中
    
    img_re = cv2.imread(img_path)
    img_re = cv2.resize(img_re, None , fx = 0.2 ,fy = 0.2 , interpolation=cv2.INTER_AREA)
    cv2.imwrite(img_path , img_re )
    
    style_img = style
    result = transfer(style_img, img_path, choice_)
    result_url = upload_photo(result)
    spent_time = (datetime.now()-spent_time).seconds
    print('花費時間:',spent_time,'秒')

    return jsonify(status = 'success!' , result = result_url)




if __name__ == '__main__':
    app.run(host="0.0.0.0" , port = 5000 , debug=True)