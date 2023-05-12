from flask import Flask, render_template, request, session
from urllib.parse import unquote as urllib_unquote
from pathlib import Path
import json
import secrets
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex()

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

@app.route("/dgd_test", methods=['POST'])
def dgd_test():
    output = request.get_json()
    result = json.loads(output)
    session["dgd_test"] = result
    return result

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