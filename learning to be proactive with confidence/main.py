from flask import Flask, render_template, request, session
from urllib.parse import unquote as urllib_unquote
from pathlib import Path
import json
import secrets
import uuid
import pyAgrum as gum
import pickle
import random

app = Flask(__name__)
app.secret_key = secrets.token_hex()

id_adn=gum.loadID("id_adn.bifxml")
ie_adn=gum.ShaferShenoyLIMIDInference(id_adn)
svc_arc = pickle.load(open("svc_arc.pickle", 'rb'))

id_tdn=gum.loadID("id_tdn.bifxml")
ie_tdn=gum.ShaferShenoyLIMIDInference(id_tdn)
svc_rtc = pickle.load(open("svc_rtc.pickle", 'rb'))

@app.template_filter('unquote')
def unquote(url):
    safe = app.jinja_env.filters['safe']
    return safe(urllib_unquote(url))

def get_data(file):
    file_json = open(file)
    data = json.load(file_json)
    return data

def save(data, file_out):
    with open(file_out, 'w') as outfile:
        outfile.write(data)

def write():
    data = []
    for txt_path in Path().glob("*.json"):
        file_json = open(txt_path)
        try:
            output = json.load(file_json)
            data.append({'score':output['partita']['score_tot'], 'level':output['partita']['livello_raggiunto'],'player':output['partecipante']})
        except json.JSONDecodeError as e:
            print(e)
    save(str(data), "player.txt")

def read():
    file = open("player.txt")
    file_content = file.read()
    output = file_content.strip('][').split('}, ')
    
    for x in range(0, len(output)-1):
        output[x] = output[x] + '}'
        output[x] = output[x].replace('\'', '"')
        output[x] = json.loads(output[x])
    output[-1] = output[-1].replace('\'', '"')
    output[-1] = json.loads(output[-1])
    return output

@app.route("/")
def home():
    file_json_it = get_data("json/italian.json")
    file_json_en = get_data("json/english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}

    write()
    return render_template("home.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/game", methods=['POST', 'GET'])
def game():
    file_json_it = get_data("json/italian.json")
    file_json_en = get_data("json/english.json")
    
    if 'language' not in session:
        session["language"] = {"language":"italian"}

    if request.method == 'POST':
        session["user_data"] = {'age': request.form["age"], 'gender': request.form["gender"], 'education': request.form["education"]}

    tmp = read()
    tmp.sort(key=lambda x: (-x.get('score'), x.get('player')))
    session["players"] = tmp[0:10]

    session["id_player"] = max({int(str(txt_path)[:-42]) for txt_path in Path().glob("*.json")}) + 1

    return render_template("game.html", player = session["id_player"], players = session["players"], data = session["user_data"], resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"], dgd_test = session["dgd_test"])

# function to return key for any value
def get_key(val, my_dict):
    tmp = []
    for key, value in my_dict.items():
        if val == value:
            tmp.append(key)
    return tmp

@app.route("/dn_test", methods=['POST'])
def dn_test():
    output = request.get_json()
    result = json.loads(output)
    dgd = get_dgd_result(session["dgd_test"]) 
    azione_pre = {'Nessuna':0, 'Corrispondenza':1, 'Errore':2, 'Aiuto':3}
    if "Azione Precedente" in result:
        pre = azione_pre[result["Azione Precedente"]]
    else:
        pre = azione_pre["Nessuna"]
    test = [[dgd["Conqueror"], dgd["Manager"], dgd["Wanderer"], dgd["Participant"], result["Sequenza"], result["Stato"], result["Carte"], pre]]
    
    ### Prediction Svc What ###
    y_predict = svc_arc.predict(test)
    prob = svc_arc.predict_proba(test)   
    if ie_adn.hasEvidence("Forecast"):
        ie_adn.chgEvidence("Forecast", prob[0])
    else:
        ie_adn.addEvidence("Forecast", prob[0])
    ie_adn.makeInference()

    decisions = ie_adn.posterior("Decision Assistance")
    index = decisions.argmax()[0].get("Decision Assistance")
    bestHelp = id_adn.variable("Decision Assistance").label(index)
    output = {}
    output["Help"] = bestHelp
    output["Input_SVC"] = test[0]
    output["Help_SVC_Decision"] = int(y_predict[0])
    output["Help_SVC_Prob"] = prob[0].tolist()
    if(bestHelp!="None"):       
        ### Prediction Svc When ###
        test[0].append(index)
        y_predict = svc_rtc.predict(test)
        prob = svc_rtc.predict_proba(test)
        if ie_tdn.hasEvidence("Forecast"):
            ie_tdn.chgEvidence("Forecast", prob[0])
        else:
            ie_tdn.addEvidence("Forecast", prob[0])
        ie_tdn.makeInference()
        
        decisions = ie_tdn.posterior("Decision Time")
        index = decisions.argmax()[0].get("Decision Time")
        bestTime = id_tdn.variable("Decision Time").label(index)
        output["Time_SVC_Decision"] = int(y_predict[0])
        output["Time_SVC_Prob"] = prob[0].tolist()
        output["Time"] = index + 2

        random.seed(random.random())
        come = random.choice(['Notifica', 'Suggerimento', 'Intervento'])
        output["How"] = come
    print(output)
    return output

@app.route("/dgd_test", methods=['POST'])
def dgd_test():
    output = request.get_json()
    result = json.loads(output)
    dgd = get_dgd_result(result) 
    keys = get_key(max(dgd.values()), dgd)
    session["profilo"] = keys
    session["dgd_test"] = result
    return result

# Calculate DGD result
def get_dgd_result(data):
    tmp = {}
    tmp["Conqueror"] = 0
    tmp["Manager"] = 0
    tmp["Wanderer"] = 0
    tmp["Participant"] = 0

    for i in data:
        if(int(i[1:])%4 == 1):
            tmp["Conqueror"] += data[i]
        elif (int(i[1:])%4 == 2):
            tmp["Manager"] += data[i]
        elif (int(i[1:])%4 == 3):
            tmp["Wanderer"] += data[i]
        else:
            tmp["Participant"] += data[i]
    return tmp

@app.route("/end")
def end():
    file_json_it = get_data("json/italian.json")
    file_json_en = get_data("json/english.json")

    if 'language' not in session:
        session["language"] = {"language":"italian"}

    return render_template("end.html", players = session["players"], user = session["user"], resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/form")
def form():
    file_json_it = get_data("json/italian.json")
    file_json_en = get_data("json/english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}

    return render_template("form.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/language", methods=['POST'])
def language():
    output = request.get_json()
    result = json.loads(output)
    session["language"] = result
    return result

@app.route("/trial")
def trial():
    file_json_it = get_data("json/italian.json")
    file_json_en = get_data("json/english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}
        
    return render_template("trial.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    result = json.loads(output) #this converts the json output to a python dictionary
    result['partecipante'] = session["id_player"]
    name = str(session["id_player"]) + "_" + str(uuid.uuid4()) + ".json"
    
    with open(name, 'a') as outfile:
        json.dump(result, outfile, indent=2)

    player = read()
    session["user"] = {'score':result['partita']['score_tot'], 'level':result['partita']['livello_raggiunto'],'player':result['partecipante']}
    player.append(session["user"])
    player.sort(key=lambda x: (-x.get('score'), x.get('player')))
    save(str(player), "player.txt")
    session["players"] = player[0:10]
    return result

if __name__ == "__main__":
    app.run(debug=True)