from flask import Flask, render_template, request, session, Response
from urllib.parse import unquote as urllib_unquote
from pathlib import Path
import json
import secrets
import uuid
import pyAgrum as gum
import pickle
from furhat_remote_api import FurhatRemoteAPI
import threading
import random 
import time

def perform_gesture():
    while True:
        time.sleep(30)
        random.seed(random.random())
        gesture = random.choice(['BigSmile', 'Blink', 'BrowRaise', 'GazeAway', 'Roll', 'Smile'])
        print(gesture)
        furhat.gesture(name=gesture)

language = 'italian'
app = Flask(__name__)
app.secret_key = secrets.token_hex()
session_result = None

id_adn=gum.loadID("id_adn.bifxml")
ie_adn=gum.ShaferShenoyLIMIDInference(id_adn)
svc_arc = pickle.load(open("svc_arc.pickle", 'rb'))

id_tdn=gum.loadID("id_tdn.bifxml")
ie_tdn=gum.ShaferShenoyLIMIDInference(id_tdn)
svc_rtc = pickle.load(open("svc_rtc.pickle", 'rb'))

# Load ID for Confidence Decision Newtork
id_cdn = gum.loadID("id_cdn.bifxml")
# Create Inference for Confidence Decision Newtork
ie_cdn = gum.ShaferShenoyLIMIDInference(id_cdn)
# Load Classifier for Confidence
svc_cc = pickle.load(open("svc_cc.pickle", 'rb'))

listen = False
# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot 
furhat = FurhatRemoteAPI(host="localhost")

@app.route("/furhat_say", methods=['POST'])
def furhat_say():
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")
    file_json = get_file_json(file_json_it, file_json_en)

    output = request.get_json()
    result = json.loads(output)
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=result["Testo"])
    except:
        print("Furhat Say:", result["Testo"])
    return result

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

def get_file_json(it, en):
    if session["language"]["language"] == "italian":
        return it
    else:
        return en

def perform_gesture():
    while True:
        time.sleep(30)
        random.seed(random.random())
        gesture = random.choice(['BigSmile', 'Blink', 'BrowRaise', 'GazeAway', 'Roll', 'Smile'])
        print(gesture)
        furhat.gesture(name=gesture)

@app.route("/")
@app.route("/home")
def home():
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}
    file_json = get_file_json(file_json_it, file_json_en)
    
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=file_json["main"]["home"])
    except:
        print("Furhat Say:", file_json["main"]["home"])

    write()
    return render_template("third_home.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route('/sse_furhat')
def sse_furhat():
    return Response(
        listen_furhat(),  # listen_furhat() is an Iterable
        mimetype='text/event-stream'  # mark as a stream response
    )

def get_file_json_lan(it, en):
    if language == "italian":
        return it
    else:
        return en

def listen_furhat():
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")  
    while True:
        file_json = get_file_json_lan(file_json_it, file_json_en)
        
        if listen==True:
            result = furhat.listen(language= file_json["language"])
            print(result)
            if(result.message in file_json["game"]["unlock"]):
                random.seed(random.random())
                gesture = random.choice(['Nod', 'Oh', 'Wink'])
                furhat.gesture(name=gesture)

                yield 'data: sblocca\n\n'
            result = ''
        else:
            break
        

@app.route("/game", methods=['POST', 'GET'])
def game():
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")  
    if 'language' not in session:
        session["language"] = {"language":"italian"}
    global language
    language = session["language"]["language"]
    file_json = get_file_json(file_json_it, file_json_en)
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=file_json["main"]["game"])
    except:
        print("Furhat Say:", file_json["main"]["game"])
    
    if request.method == 'POST':
        session["user_data"] = {'age': request.form["age"], 'gender': request.form["gender"], 'education': request.form["education"]}

    tmp = read()
    tmp.sort(key=lambda x: (-x.get('score'), x.get('player')))
    session["players"] = tmp[0:10]

    session["id_player"] = max({int(str(txt_path)[:-42]) for txt_path in Path().glob("*.json")}) + 1

    global listen 
    listen = True
    threading.Thread(target = sse_furhat).start()

    return render_template("third_game.html", player = session["id_player"], players = session["players"], data = session["user_data"], resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"], dgd_test = session["dgd_test"])

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
    
    # Prediction Probabilities from Assistance Requested Classifier
    y_predict = svc_arc.predict(test)
    prob = svc_arc.predict_proba(test)  
    print(test, y_predict, prob) 
    if ie_adn.hasEvidence("Forecast"):
        ie_adn.chgEvidence("Forecast", prob[0])
    else:
        ie_adn.addEvidence("Forecast", prob[0])
    ie_adn.makeInference()

    decisions = ie_adn.posterior("Decision Assistance")
    index = decisions.argmax()[0].get("Decision Assistance")
    bestHelp = id_adn.variable("Decision Assistance").label(index)
    print("What:", decisions, index, bestHelp)
    output = {}
    output["Help"] = bestHelp
    output["Input_SVC"] = test[0]
    output["Help_SVC_Decision"] = int(y_predict[0])
    output["Help_SVC_Prob"] = prob[0].tolist()
    if(bestHelp!="None"):       
        # Prediction Probabilities from Request Time Classifier
        test[0].append(index)
        y_predict = svc_rtc.predict(test)
        prob = svc_rtc.predict_proba(test)
        print(test, y_predict, prob)
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
        print("When:", decisions, index, bestTime, index + 2)

        test[0].append(index+2)
        # Prediction Probabilities from Confidence Classifier
        y_predict = svc_cc.predict(test)
        prob = svc_cc.predict_proba(test)   
        print(test, y_predict, prob)
        # Set Evidence with Proba
        if ie_cdn.hasEvidence("Forecast"):
            ie_cdn.chgEvidence("Forecast", prob[0])
        else:
            ie_cdn.addEvidence("Forecast", prob[0])
        # Make Inference
        ie_cdn.makeInference()
        # Get Decision
        decisions = ie_cdn.posterior("Decision Confidence")
        index = decisions.argmax()[0].get("Decision Confidence")
        confidence = id_cdn.variable("Decision Confidence").label(index)
        print("How:", decisions, index, confidence)
        output["How_SVC_Decision"] = int(y_predict[0])
        output["How_SVC_Prob"] = prob[0].tolist()
        output["How"] = confidence
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
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")

    if 'language' not in session:
        session["language"] = {"language":"italian"}
    file_json = get_file_json(file_json_it, file_json_en)
    
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=file_json["main"]["end"])
    except:
        print("Furhat Say:", file_json["main"]["end"])
    return render_template("third_end.html", players = session["players"], user = session["user"], resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/form")
def form():
    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}
    file_json = get_file_json(file_json_it, file_json_en)
    
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=file_json["main"]["form"])
    except:
        print("Furhat Say:", file_json["main"]["form"])

    return render_template("third_form.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/final_form")
def final_form():
    global listen 
    listen = False

    file_json_it = get_data("json/third_italian.json")
    file_json_en = get_data("json/third_english.json")
    if 'language' not in session:
        session["language"] = {"language":"italian"}
    file_json = get_file_json(file_json_it, file_json_en)
    
    try:
        # Set the voice of the robot
        furhat.set_voice(name= file_json["main"]["voice"])
        furhat.say(text=file_json["main"]["final_form"])
    except:
        print("Furhat Say:", file_json["main"]["final_form"])
    
    return render_template("third_final_form.html", resObj_it=file_json_it,  resObj_en=file_json_en, actual_language =  session["language"])

@app.route("/language", methods=['POST'])
def language():
    output = request.get_json()
    result = json.loads(output)
    session["language"] = result
    global language
    language = session["language"]["language"]
    return result

@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    result = json.loads(output) #this converts the json output to a python dictionary
    global session_result
    session_result = result
    #session['result'] = result

    return result

@app.route('/save_data', methods=['POST'])
def save_data():
    output = request.get_json()
    result = json.loads(output) #this converts the json output to a python dictionary
    session_result['partecipante'] = session["id_player"]
    session_result['post_interaction'] = result
    id4 = str(uuid.uuid4())
    name = str(session["id_player"]) + "_" + str(id4) + ".json"
    name2 = "./data_proactive/" + str(session["id_player"]) + "_" + str(id4) + ".json"

    with open(name, 'a') as outfile:
        json.dump(session_result, outfile, indent=2)

    with open(name2, 'a') as outfile:
        json.dump(session_result, outfile, indent=2)

    player = read()
    session["user"] = {'score':session_result['partita']['score_tot'], 'level':session_result['partita']['livello_raggiunto'],'player':session_result['partecipante']}
    player.append(session["user"])
    player.sort(key=lambda x: (-x.get('score'), x.get('player')))
    save(str(player), "player.txt")
    session["players"] = player[0:10]

    return result


if __name__ == "__main__":
    app.run(debug=True)
    threading.Thread(target = perform_gesture).start()

