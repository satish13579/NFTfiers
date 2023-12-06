from flask import Flask, request,session,render_template
from algosdk.v2client import algod,indexer
from algosdk import account, mnemonic, encoding
from algosdk import util,transaction,error
from beaker import client,sandbox,consts
import contract
import json,base64
from flask_cors import CORS
import base64
from PIL import Image, ImageDraw, ImageFont
import datetime
import qrcode
import requests,hashlib

##### GLOBAL CONSTANTS ##########
INDEXER_ENDPOINT="https://testnet-algorand.api.purestake.io/idx2"
ALGOD_ENDPOINT="https://testnet-algorand.api.purestake.io/ps2"
APP_ID="<APP ID>"
API_KEY="<PURESTAKE API KEY>"
CREATOR_ADDRESS="<APP CREATER ADDRESS>"
TOKEN=''
HEADERS = {
        "X-API-Key": API_KEY,
    }
DEPLOYED_URL="http://127.0.0.1:5000/"
PINATA_JWT="<PINATA JWT>"
PINATA_KEY="<PINATA KEY>"
PINATA_SECRET_KEY="<PINATA SECRET KEY>"
#################################


app = Flask(__name__)
app.secret_key = 'algo-project'
CORS(app,resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    upk=session.get('upk')
    upubk=session.get('upubk')
    if upk and upubk:
        if(upubk==CREATOR_ADDRESS):
            return render_template('Home.html',role="ADMIN")
        else:
            return render_template('Home.html',role="STUDENT")
    else:
        return render_template('Home.html',role="NONE")

@app.route('/student')
def student(): 
    upk=session.get('upk')
    upubk=session.get('upubk')
    if upk and upubk:
        if(upubk!=CREATOR_ADDRESS):
            return render_template('myprofile.html')
        else:
            return render_template('Home.html',role="NONE")
    else:
        return render_template('Home.html',role="NONE")
    

@app.route('/university')
def university(): 
    return render_template('students.html')

@app.route('/aboutus')
def aboutus():
    return render_template('about us.html')

@app.route('/documents',methods=['GET'])
def documents():
    return render_template("documents.html")

# @app.route('/uc')
# def uc():
#     return render_template('upload_certificate.html')

@app.route('/au',methods=['POST'])
def au():
    upk=session.get('upk')
    upubk=session.get('upubk')
    if upk and upubk:
        if upubk==CREATOR_ADDRESS:
            address=request.form.get('address')
            name=request.form.get('name')
            rollno=request.form.get('rollno')
            branch=request.form.get('branch')

            algod_client = algod.AlgodClient(TOKEN,ALGOD_ENDPOINT,HEADERS)
            indexer_client = indexer.IndexerClient(TOKEN, INDEXER_ENDPOINT, HEADERS)

            pk=session.get('upk')
            pubk=session.get('upubk')

            acct=sandbox.SandboxAccount(address=pubk,private_key=pk)
            app_client = client.ApplicationClient(
                algod_client, contract.app,app_id=APP_ID, signer=acct.signer
            )
            try:
                boxes = [(0, encoding.decode_address(address))]
            except error.WrongKeyLengthError as e:
                return json.dumps({"status":False,"notify":"Enter a Valid Public Key"})
            
            res=app_client.call(contract.add_user,sender=pubk,user_address=address,rollno=rollno,name=name,branch=branch, boxes=boxes)
            if(res.raw_value[2:]==bytes("Only the application creator can add users",'utf-8')):
                return json.dumps({"status":False,"notify":"Only the application creator can Add Users"})
            elif(res.raw_value[2:]==bytes("User Already Exists",'utf-8')):
                return json.dumps({"status":False,"notify":"User with this Public Address Already Exists"})
            elif(res.raw_value[2:]==bytes("User address added successfully",'utf-8')):
                return json.dumps({"status":True,"notify":"User Added Successfully"})
            else:
                return json.dumps({"status":False,"notify":"Something went Wrong!!"})
        else:
            return json.dumps({"status":False,"notify":"Only Admin Can Add Students"})
    else:
        return json.dumps({"status":False,"notify":"Session Expired, Please Login Again to Add Students"})
    
@app.route('/make_grad',methods=["POST"])
def make_grad():
    pubk=session.get("upubk")
    pk=session.get("upk")
    user_address=request.form.get("user_address")
    print(user_address)
    algod_client=algod.AlgodClient(TOKEN,ALGOD_ENDPOINT,HEADERS)
    acct=sandbox.SandboxAccount(address=pubk,private_key=pk)
    app_client = client.ApplicationClient(
                algod_client, contract.app,app_id=APP_ID, signer=acct.signer,sender=pubk
            )
    res=app_client.call(contract.make_grad,
                        sender=pubk,
                        user_address=encoding.decode_address(user_address),
                        boxes=[(0,encoding.decode_address(user_address))])
    if(res.raw_value[2:]==bytes("Box has No Value","utf-8")):
       return json.dumps({"status":False,"notify":"Invalid User"})
    elif(res.raw_value[2:]==bytes("User is Already Grad","utf-8")):
        return json.dumps({"status":False,"notify":"This User is Already Graduated"})
    elif(res.raw_value[2:]==bytes("Made this user Graduated","utf-8")):
        return json.dumps({"status":True,"notify":"Made This User Graduated"})
    else:
        return json.dumps({"status":False,"notify":"Something Went Wrong"})


def replace_timestamp(st:bytes):
    times=st.split("~".encode('utf-8'))
    times=times[0]
    times1=times[2:] #stripped string
    times=times1.split("join_timestamp\":\"".encode('utf-8'))
    ts=times[1][0:8] #should be removed
    # tim1=times.split("\",\"join_timestamp\":\"".encode('utf-8'))[0]

    inter=int.from_bytes(times[1][0:8],"big") #should be added
    times2=times1.split(ts)
    if(times1[19]==49):
        sd=times1.split("\",\"gradts\":\"".encode('utf-8'))
        sd=sd[1]
        sd=sd[0:8] #should be removed
        si=int.from_bytes(sd,'big') #should be added
        s=times1.split(sd)
        gh=s[1]
        gh=gh.split(ts)
        res=s[0].decode('utf-8')+str(si)+gh[0].decode('utf-8')+str(inter)+gh[1].decode('utf-8')
        return res
    res=times2[0].decode('utf-8')+str(inter)+times2[1].decode("utf-8")
    # st.replace(bytes("~"),bytes(''))
    return res

def replace_timestamp2(st:bytes):
    times=st.split("~".encode('utf-8'))
    times1=times[0]
    # times1=times[2:] #stripped string
    times=times1.split("join_timestamp\":\"".encode('utf-8'))
    ts=times[1][0:8] #should be removed
    # tim1=times.split("\",\"join_timestamp\":\"".encode('utf-8'))[0]

    inter=int.from_bytes(times[1][0:8],"big") #should be added
    times2=times1.split(ts)
    if(times1[19]==49):
        sd=times1.split("\",\"gradts\":\"".encode('utf-8'))
        sd=sd[1]
        sd=sd[0:8] #should be removed
        si=int.from_bytes(sd,'big') #should be added
        s=times1.split(sd)
        gh=s[1]
        gh=gh.split(ts)
        res=s[0].decode('utf-8')+str(si)+gh[0].decode('utf-8')+str(inter)+gh[1].decode('utf-8')
        return res
    res=times2[0].decode('utf-8')+str(inter)+times2[1].decode("utf-8")
    # st.replace(bytes("~"),bytes(''))
    return res

def pin_json(json_):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    res=dict()
    res['pinataContent']=json_
    payload = json.dumps(res)
    headers = {
    'Content-Type': 'application/json',
    'pinata_api_key': PINATA_KEY,
    'pinata_secret_api_key': PINATA_SECRET_KEY 
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def create_pin_certificate(img_name):

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    payload={'pinataOptions': '{"cidVersion": 1}',
    'pinataMetadata': '{"name":"'+img_name+'", "keyvalues": {"company": "Pinata"}}'}

    files=[
    ('file',(img_name,open('./docs/'+img_name,'rb'),'application/octet-stream'))
    ]
    headers = {
    'pinata_api_key': PINATA_KEY,
    'pinata_secret_api_key': PINATA_SECRET_KEY 
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return json.loads(response.text)


def create_graduation_certificate(name,rollno,branch,gradts,user_address,id):
    template_path = "1.png"
    template_image = Image.open(template_path)
    draw = ImageDraw.Draw(template_image)
    font_path = "arial.ttf"  # Path to the font file
    font_size = 46
    font = ImageFont.truetype(font_path, font_size)
    fields = {
    "rollno": rollno,
    "branch": branch,
    "date_month": datetime.date.fromtimestamp(int(gradts)).strftime("%B %d, %Y"),
    }
    positions = {
        "rollno": (324, 1116),
        "branch": (1105, 1116),
        "date_month": (678, 1444),
    }
    text_color = (255, 255, 255)  # RGB color (white in this example)
    date_pos=(256, 1624)
    date_v=datetime.date.fromtimestamp(int(gradts)).strftime("%d-%m-%Y")
    draw.text(date_pos,date_v,fill=text_color,font=ImageFont.truetype(font_path, 56),align=['center'])
    name_pos=(707,940)
    name=name
    text_width, text_height = draw.textsize(name, font=ImageFont.truetype(font_path, 70))
    name_pos = (name_pos[0] - text_width / 2, name_pos[1] - text_height / 2)
    draw.text(name_pos,name,fill=text_color,font=ImageFont.truetype(font_path, 70),align='center')
    for field, position in positions.items():
        text = fields[field]
        draw.text(position, text, font=font, fill=text_color)
    url = DEPLOYED_URL+'view_doc.html?user_address='+user_address+"&id="+str(id)  # Replace with your desired URL
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Resize the QR code to fit in the template
    qr_image = qr_image.resize((160, 160))
    template_image.paste(qr_image, (630, 1760))
    # Save the modified image
    output_path = "./docs/{}-{}.png".format("Graduation_Certificate",user_address)
    template_image.save(output_path)
    return "{}-{}.png".format("Graduation_Certificate",user_address)

def create_digest(json_):
    # Convert the metadata to a JSON string
    metadata_json = json.dumps(json_)

    # Compute the SHA-256 digest
    hash_object = hashlib.sha256(metadata_json.encode("utf-8"))
    digest = hash_object.digest()

    # Print the digest as a hexadecimal string
    return digest.hex()

def find_subsequence(main_bytes, sub_bytes):
    position = main_bytes.find(sub_bytes)
    if position == -1:
        return 999
    return position-2

@app.route('/upcert',methods=["POST"])
def upcert():
    pubk=session.get('upubk')
    pk=session.get('upk')
    if pk and pubk:
        if session.get('upubk')==CREATOR_ADDRESS:
            user_address=request.form.get('user_address')
            typ=request.form.get('type')
            algod_client=algod.AlgodClient(TOKEN,ALGOD_ENDPOINT,HEADERS)
            indexer_client=indexer.IndexerClient(TOKEN,INDEXER_ENDPOINT,HEADERS)

            acct=sandbox.SandboxAccount(address=pubk,private_key=pk)
            app_client = client.ApplicationClient(
                algod_client, contract.app,app_id=APP_ID, signer=acct.signer
            )

            if(typ=='grad_cert'):
                box=app_client.call(contract.get_user,pubk,user_address=encoding.decode_address(user_address),boxes=[(0,encoding.decode_address(user_address))])
                cleaned_str=replace_timestamp(box.raw_value)
                user_data=json.loads(cleaned_str)
                if(user_data['grad']['isgrad']=='1'):
                    img_name=create_graduation_certificate(user_data['name'],user_data['rollno'],user_data['branch'],user_data['grad']['gradts'],user_address,len(user_data['certificates']))
                    res=create_pin_certificate(img_name)
                    if(res['IpfsHash']):
                        metadata=dict()
                        metadata['standard']='arc71'
                        metadata['owner']=user_address
                        metadata['issuer']=pubk
                        metadata['description']='Graduation Certificate in '+user_data['branch']+' For '+user_data['rollno']+'Rollno.'
                        metadata['external_url']="ipfs://"+res['IpfsHash']+"#i"
                        metadata['properties']=dict()
                        metadata['properties']['Duration']=datetime.date.fromtimestamp(int(user_data['join_timestamp'])).strftime("%d-%m-%Y")+" "+datetime.date.fromtimestamp(int(user_data['grad']['gradts'])).strftime("%d-%m-%Y")
                        metadata['properties']['Curriculum Mode']="Offline"
                        metadata['properties']['CGPA']="8.91"
                        metadata['mime_type']='image/x-png'
                        jsres=pin_json(metadata)
                        if(jsres['IpfsHash']):
                            digest=create_digest(metadata)
                            nft_mint=transaction.AssetCreateTxn(CREATOR_ADDRESS,algod_client.suggested_params(),1,0,False,freeze=CREATOR_ADDRESS,unit_name="GC",asset_name="Graduation_cert-"+user_data['rollno'],url="ipfs://"+res['IpfsHash'],metadata_hash=bytes.fromhex(digest))
                            signed_nft_mint=nft_mint.sign(pk)
                            tx_id = algod_client.send_transaction(signed_nft_mint) 
                            results = transaction.wait_for_confirmation(algod_client, tx_id,4)
                            
                            created_asset = results["asset-index"]
                            
                            cert='"{}":'.format(created_asset)+json.dumps(metadata)
                            print(cert)
                            subs='"...":"..."}}'
                            subs=subs.encode('utf-8')
                            pos=find_subsequence(box.raw_value,subs)
                            if(pos!=999):
                                add_res=app_client.call(contract.add_certificate,CREATOR_ADDRESS,acct.signer,algod_client.suggested_params(),user_address=user_address,cert=cert,pos=pos,boxes=[(0,encoding.decode_address(user_address))])
                                print(add_res.raw_value)
                                if(add_res.raw_value[2:]==bytes("Substring Not Matched","utf-8")):
                                    return json.dumps({"status":False,"notify":"Adding Certificate to Box Failed, Due To Substring Mismatch"})
                                elif(add_res.raw_value[2:]==bytes("Box has No Value","utf-8")):
                                    return json.dumps({"status":False,"notify":"No Box Found For This User"})
                                elif(add_res.raw_value[2:]==bytes("Certificate Added","utf-8")):
                                    return json.dumps({"status":True,"notify":"Certificate Added Successfully"})
                            else:
                                return json.dumps({"status":False,"notify":"Adding Certificate to Box Failed, Due To Substring Mismatch"})
                        else:
                            return json.dumps({"status":False,"notify":"Failed Uploading MetaData of NFT"})
                    else:
                        return json.dumps({"status":False,"notify":"Failed Uploading Image of NFT"})
                else:
                    return json.dumps({"status":False,"notify":"Please Graduate Him First To Certificate"})
            else:
                return json.dumps({"status":False,"notify":"Unknown Certificate Type"})

        else:
            return json.dumps({"status":False,"notify":"Only Admin can add Certificates"})
    return json.dumps({"status":False,"notify":"Session Expired, Please Login Again to Add Certificates"})                         

@app.route('/get_user2',methods=['POST'])
def get_user2():
    pk=session.get('upk')
    pubk=session.get("upubk")
    if pk and pubk:
        user_address=request.form.get("user_address")
        algod_client = algod.AlgodClient(TOKEN,ALGOD_ENDPOINT, HEADERS)
        acct=sandbox.SandboxAccount(address=pubk,private_key=pk)
        app_client = client.ApplicationClient(
            algod_client, contract.app,app_id=APP_ID, signer=acct.signer
        )
        res=app_client.call(contract.get_user,pubk,user_address=encoding.decode_address(user_address),boxes=[(0,encoding.decode_address(user_address))])
        cleaned_str=replace_timestamp(res.raw_value)
        return cleaned_str
    else:
        return json.dumps({"status":False,"notify":"Session Expired, Please Login Again to Add Certificates"}) 

@app.route('/get_user',methods=['GET'])
def get_user():
    pk=session.get('upk')
    pubk=session.get("upubk")
    if pk and pubk:
        user_address=pubk
        algod_client = algod.AlgodClient(TOKEN,ALGOD_ENDPOINT, HEADERS)
        acct=sandbox.SandboxAccount(address=pubk,private_key=pk)
        app_client = client.ApplicationClient(
            algod_client, contract.app,app_id=APP_ID, signer=acct.signer
        )
        res=app_client.call(contract.get_user,pubk,user_address=encoding.decode_address(user_address),boxes=[(0,encoding.decode_address(user_address))])
        cleaned_str=replace_timestamp(res.raw_value)
        return cleaned_str
    else:
        return json.dumps({"status":False,"notify":"Session Expired, Please Login Again to Add Certificates"})   

@app.route("/get_students",methods=['POST'])
def get_students():
    pubk=session.get('upubk')
    pk=session.get('upk')
    if pk and pubk:
        if session.get('upubk')==CREATOR_ADDRESS:
            indexer_client=indexer.IndexerClient(TOKEN,INDEXER_ENDPOINT,HEADERS)
            boxes=indexer_client.application_boxes(APP_ID)
            b=[]
            for i in boxes['boxes']:
                b.append(base64.b64decode(i['name']))
                stds=dict()
                stds['students']=[]
            for i in b:
                std=indexer_client.application_box_by_name(APP_ID,i)
                val=base64.b64decode(std['value'])
                cleaned_str=replace_timestamp2(val)
                user_data=json.loads(cleaned_str)
                user_data['address']=encoding.encode_address(i)
                stds['students'].append(user_data)
            return json.dumps({"status":True,"data":stds})

        else:
            return json.dumps({"status":False,"notify":"Only Admin can Fetch Students"})
    return json.dumps({"status":False,"notify":"Session Expired, Please Login Again to Add Certificates"})   

@app.route('/login', methods=['POST'])
def login():
    indexer_client = indexer.IndexerClient(TOKEN,INDEXER_ENDPOINT, HEADERS)
    aps=indexer_client.applications(APP_ID)
    creator=aps['application']['params']['creator']
    
    # Get the mnemonic from the request parameters
    mnemoni = request.form.get('mnemonic')
    # # Derive the private key from the mnemonic
    try:
        private_key = mnemonic.to_private_key(mnemoni)
    except Exception as e:
        print(e)
        return json.dumps({"status":False,"notify":"Given mnemonic is Invalid"})
    # # Return the public address corresponding to the private key
    public_address = account.address_from_private_key(private_key)

    if(public_address==creator):
        session['upk']=private_key
        session['upubk']=public_address
        return json.dumps({"status":True,"role":"admin","notify":"Logging as Admin"})
    else:
        boxes=indexer_client.application_boxes(APP_ID)
        b=[]
        for i in boxes['boxes']:
            b.append(encoding.encode_address(base64.b64decode(i['name'])))
        if public_address in b:
            session['upk']=private_key
            session['upubk']=public_address
            return json.dumps({"status":True,"role":"user","notify":"Logging as User [{}]".format(public_address)})
        else:
            return json.dumps({"status":False,"notify":"Your Address is not Verified By Admin"})
        # return json.dumps({"status":False,"notify":"Given mnemonic is Not Owned By University"})
    
@app.route('/logout', methods=['GET'])
def logout():
    if session.get('upk') and session.get('upubk'):
        session.pop('upk')
        session.pop('upubk')
        return json.dumps({"status":True})
    else:
        return json.dumps({"status":False,"notify":"Please Login First.!!"})



if __name__ == '__main__':
    app.run(debug=True)
