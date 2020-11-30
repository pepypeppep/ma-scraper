import os
from flask import Flask, render_template, request
from pyhocon import ConfigFactory
import csv
import http.client
import json
from datetime import date, datetime
import multiprocessing

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'documents')
CONFIG_FOLDER = os.path.join(APP_ROOT, 'config')

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONFIG_FOLDER'] = CONFIG_FOLDER

conf = ConfigFactory.parse_file(app.config['CONFIG_FOLDER']+'/apikey.conf')

@app.route('/', methods=['GET', 'POST'])
def index(result=None):
    q = multiprocessing.Queue()
    if request.args.get('year', None):
        p1 = multiprocessing.Process(target=crawler, args=(request.args['year'], q))
        # result = crawler(request.args['year'])
        p1.start()
        p1.join()
        result = q.get()
    return render_template('index.html', result=result)

def crawler(year, q):
    fname = str(datetime.now()) + '-MA-(data for '+year+').json'
    conn = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")
    conn2 = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")
    conn3 = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")
    conn4 = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")

    payload = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+")&attributes=Id,Ti,Ty,Y,CC,J.JN,J.JId,AA.AuN,AA.AuId,AA.AfN,AA.AfId,C.CN,DOI,Pt&offset=1&count=1000"
    payload2 = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+")&attributes=Id,Ti,Ty,Y,CC,J.JN,J.JId,AA.AuN,AA.AuId,AA.AfN,AA.AfId,C.CN,DOI,Pt&offset=1001&count=1000"
    payload3 = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+")&attributes=Id,Ti,Ty,Y,CC,J.JN,J.JId,AA.AuN,AA.AuId,AA.AfN,AA.AfId,C.CN,DOI,Pt&offset=2001&count=1000"
    payload4 = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+")&attributes=Id,Ti,Ty,Y,CC,J.JN,J.JId,AA.AuN,AA.AuId,AA.AfN,AA.AfId,C.CN,DOI,Pt&offset=3001&count=1000"
    # payload = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+",Pt='3')&attributes=Id,Ti,Ty,Y,CC,J.JN,J.JId,AA.AuN,AA.AfN,C.CN,DOI&offset=0&count=1000"

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'ocp-apim-subscription-key': conf.get_string("APIkey.key"),
    }

    conn.request("POST", "/academic/v1.0/evaluate", payload, headers)
    conn2.request("POST", "/academic/v1.0/evaluate", payload2, headers)
    conn3.request("POST", "/academic/v1.0/evaluate", payload3, headers)
    conn4.request("POST", "/academic/v1.0/evaluate", payload4, headers)

    response = conn.getresponse()
    response2 = conn2.getresponse()
    response3 = conn3.getresponse()
    response4 = conn4.getresponse()
    v = json.loads(response.read().decode("utf-8"))
    v2 = json.loads(response2.read().decode("utf-8"))
    v3 = json.loads(response3.read().decode("utf-8"))
    v4 = json.loads(response4.read().decode("utf-8"))
    no = 1
    docType = ''
    allData = v['entities']+v2['entities']+v3['entities']+v4['entities']

    with open(os.path.join(app.config['UPLOAD_FOLDER'], fname), mode='w') as f:
        # f.write(allData)
        #f.write(str(allData))
	    json.dump(allData, f)
    q.put(fname)
    return fname

if __name__ == '__main__':
    app.run(host='0.0.0.0')
