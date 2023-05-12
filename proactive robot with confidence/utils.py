import json
import math
import pickle
import random
import numpy as np
import pandas as pd
import pyAgrum as gum
import pyAgrum.lib.image as gumimage
from matplotlib import pyplot as plt
from pathlib import Path
from datetime import datetime
from imblearn.over_sampling import SMOTE
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score

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

# Plot utility function for ID
def plot_utility_function(x_start, x_stop, y_bottom, y_top, function):
    # Return evenly spaced numbers calculated over the interval [start, stop].
    # X-values
    x = np.linspace(x_start, x_stop, dtype=int)
    # set Y-axis limits 
    plt.ylim(y_bottom, y_top)
    # Plot the function
    plt.plot(x, function(x), color='red')
    # Add vertical lines in X-coordinate
    plt.axvline(0, c='k', linestyle='--')
    # Each value is represented by a dot
    plt.scatter(x, function(x), marker='o')
    # Set Labels
    plt.ylabel("Utility")
    plt.xlabel("Distance")
    # Show Plot
    plt.show()
  
# Example of Final Decision System Implementation
def decision_system(player_profile, game_state):
  # Create test
  test = [[player_profile["Conqueror"], player_profile["Manager"], player_profile["Wanderer"], player_profile["Participant"], game_state["Sequence"], game_state["State"], game_state["Deck"], game_state["PriorAction"]]]

  # Load ID for Assistance Decision Newtork
  id_adn = gum.loadID("id_adn.bifxml")
  # Create Inference for Assistance Decision Newtork
  ie_adn = gum.ShaferShenoyLIMIDInference(id_adn) 
  # Load Classifier for Assistance Requested
  svc_arc = pickle.load(open("svc_arc.pickle", 'rb'))

  # Prediction Probabilities from Assistance Requested Classifier
  proba = svc_arc.predict_proba(test)   
  # Set Evidence with Proba
  ie_adn.addEvidence("Forecast", proba[0])
  # Make Inference
  ie_adn.makeInference()
  # Get Decision
  decisions = ie_adn.posterior("Decision Assistance")
  index = decisions.argmax()[0].get("Decision Assistance")
  assistance = id_adn.variable("Decision Assistance").label(index)

  # If assistance
  if(assistance!="None"):       
    # Append Decided Assistance
    test[0].append(index)

    # Load ID for Time Decision Newtork
    id_tdn = gum.loadID("id_tdn.bifxml")
    # Create Inference for Time Decision Newtork
    ie_tdn = gum.ShaferShenoyLIMIDInference(id_tdn)
    # Load Classifier for Request Time
    svc_rtc = pickle.load(open("svc_rtc.pickle", 'rb'))

    # Prediction Probabilities from Request Time Classifier
    proba = svc_rtc.predict_proba(test)   
    # Set Evidence with Proba
    ie_tdn.addEvidence("Forecast", proba[0])
    # Make Inference
    ie_tdn.makeInference()
    # Get Decision
    decisions = ie_tdn.posterior("Decision Time")
    index = decisions.argmax()[0].get("Decision Time")
    time = index + 2

    # Append Decided Time
    test[0].append(time)

    # Load ID for Confidence Decision Newtork
    id_cdn = gum.loadID("id_cdn.bifxml")
    # Create Inference for Confidence Decision Newtork
    ie_cdn = gum.ShaferShenoyLIMIDInference(id_cdn)
    # Load Classifier for Confidence
    svc_cc = pickle.load(open("svc_cc.pickle", 'rb'))

    # Prediction Probabilities from Confidence Classifier
    proba = svc_cc.predict_proba(test)   
    # Set Evidence with Proba
    ie_cdn.addEvidence("Forecast", proba[0])
    # Make Inference
    ie_cdn.makeInference()
    # Get Decision
    decisions = ie_cdn.posterior("Decision Confidence")
    index = decisions.argmax()[0].get("Decision Confidence")
    confidence = index + 1

    return assistance, time, confidence
  else:
    return assistance

##################################################################################################

# Get Data for each Confidence
def get_data(write, data, confidence_val):
  # Prior Action
  # Nessuna: None, Corrispondenza: Match, Errore: Mistake, Aiuto: Assistance
  dict_pa = {
    'Nessuna':0, 
    'Corrispondenza':1, 
    'Errore':2, 
    'Aiuto':3}
  # Assistance Requested 
  # Nessuna: None, Nascondi Carta: Hide Card, Suggerisci Posizione: Suggest Position, 
  # Indica Posizione: Indicate Position, Rivedi Sequenza: Review Sequence
  dict_ar = {
    'Nessuno': 0,
    'Nascondi Carta': 1,
    'Suggerisci Posizione': 2,
    'Indica Posizione': 3, 
    'Rivedi Sequenza': 4}
  # Confidence
  # Notifica: Notification, Suggerimento: Tip, Intervento: Action
  dict_conf = {
    'Notifica':1, 
    'Suggerimento':2, 
    'Intervento':3}
  set_assistance = [
    'Nascondi Carta', 
    'Suggerisci Posizione', 
    'Indica Posizione', 
    'Rivedi Sequenza']
  active_write = False

  # Get DGD's result of each player type
  dgd = get_dgd_result(data["dgd_test"])

  dict_level = data["partita"]["livello"]
  # For each level 
  for level_loop in range(1, len(dict_level)+1):
    level = str(level_loop)
    if(level in dict_level.keys()): 
      # Reset Old Action 
      old_action = ''
      # Reset Prior Action
      prior_actions = ["Nessuna"]

      # For each state
      dict_state = dict_level[level]["sequenza"]
      # Set number of cards of sequence to remember
      n_sequence = dict_level[level]["n_sequenza"] 
      for state_ in range(0, len(dict_state.keys())):
        state = str(state_)
        # Set number of deck cards to choose from
        n_deck_cards = dict_level[level]["n_carte"]
        moves_dict = dict_state[state]["mossa"]
        # For each action
        for move_loop in range(0, len(moves_dict)):
          move = str(move_loop)
          # Set Action
          action = moves_dict[move]
          # Set Assistance Requested
          action_type = action["tipo"]

          # Set Prior Action
          if(action_type in set_assistance):
            prior_actions.append('Aiuto')
          elif(action_type=='Errore'):
            prior_actions.append('Errore')
          elif(action_type=='Corrispondenza'):
            prior_actions.append('Corrispondenza')

          if action_type == "ID" and action["decisione_aiuto"] in set_assistance and action["random_come"]==confidence_val:
            # Decision ID
            id_decision = action
            active_write = False
          elif action_type == confidence_val:
            # Confidence Activated
            active_write = True
            # Update Old Action with the new one 
            old_action = action["aiuto"]
          elif action_type == "Aiuti Sbloccati":
            pass
          elif action_type == old_action and confidence_val == "Intervento":
            # Action
            pass
          elif active_write == True:
            # Assistance Activated
            # Set Confidence
            confidence = dict_conf[confidence_val]
            # User: Liked -> Major Confidence (Notification/Tip)
            if action_type == old_action:
              # Change Confidence
              confidence += 1
            else:
              # User: Unliked -> Minor Confidence (Tip)
              if confidence_val == "Suggerimento":
                confidence -= 1
              elif confidence_val == "Intervento":                                
                if action_type == "Non Gradito":
                  confidence -= 1
                elif action_type == "Gradito":
                  pass
                else:
                  # Confidence cannot be evaluated
                  active_write = False

            if active_write == True:
              # Set Decision Assistance
              value_request = dict_ar[id_decision['decisione_aiuto']]
              # Set Decision Time
              bin_time = id_decision["decisione_tempo"]
              # Set Prior Action
              val_prior_action = dict_pa[prior_actions[-2]]

              # Write the row on array
              write.append([dgd["Conqueror"], dgd["Manager"], dgd["Wanderer"], dgd["Participant"], n_sequence, state_+1, n_deck_cards, val_prior_action, value_request, bin_time, confidence])
          
            # Reset 
            id_decision = {}
            old_action = ''
            active_write = False
        else:
            # Reset 
            old_action = ''
            active_write = False

        # If the move is one the assistances that changes the number of deck cards
        if action_type in set_assistance[:3]:
          # Update number of deck cards
          n_deck_cards = moves_dict[move]["nCarte_nonNascoste_dopo"]

  return write

# Get Dataset for Confidence Classification 
def get_data_cc():
  write = []

  for txt_path in Path("./data/").glob("*.json"):
    # Get data from file
    file_json = open(txt_path)
    data = json.load(file_json)

    # Get Data - Confidence: Notification
    # Liked: Confidence += 1
    # Unliked: Confidence 
    write = get_data(write, data, "Notifica")

    # Get Data - Confidence: Tip
    # Liked: Confidence += 1
    # Unliked: Confidence -= 1
    write = get_data(write, data, "Suggerimento")

    # Get Data - Confidence: Action
    # Liked: Confidence 
    # Unliked: Confidence -= 1
    write = get_data(write, data, "Intervento")

  # Convert array to Pandas DataFrame
  df = pd.DataFrame(write, columns = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested", "Bin", "Confidence"])
  # Drop Duplicates
  df.drop_duplicates(subset=None, inplace=True)
  # Write data into file CSV
  df.to_csv('dataset_cc.csv', index=False, sep=",")

# Update Dataset for Confidence Classification 
def update_data_cc(data):
  # Define target name
  y = 'Confidence'
  # Split the dataset by class
  # Reduction of Class Notification
  df1 = data[data[y]==1].sample(n=115, random_state=None)
  # Reduction of Class Tip
  df2 = data[data[y]==2].sample(frac=1, random_state=None)
  # Class Action
  df3 = data[data[y]==3].sample(n=105, random_state=None)
  #print(df3)

  # Extract Test Set: 10 elements of each class
  df_test = pd.concat([df1[:10], df2[:10], df3[:10]]).sample(frac=1)

  # Extract Train Set
  df_train = pd.concat([df1[10:], df2[10:], df3[10:]]).sample(frac=1) 

  return df_train, df_test

# SVM Multiclass Classification for Confidence
def confidence_classification():
  # Import the dataset
  dataset = pd.read_csv('dataset_cc.csv',delimiter= ',')

  column = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested", "Bin", "Confidence"]
  max_acc = 0
  # Repeat the process to get the best accuracy
  for i in range(0,200):
    # Get updated train and test set
    train, test= update_data_cc(dataset)
   
    # Split train set in feature and target (bin)
    x_train = train.iloc[:,0:10].values.astype(float)
    y_train = train.iloc[:,10:11].values.astype(float)

    # Define SVC
    svc = make_pipeline(StandardScaler(), SVC(gamma='auto', probability=True))
    # Fit data to StandardScaler
    svc.fit(x_train, y_train.ravel())
    # Cross-validation on train set
    cross_val_score(svc, x_train, y_train.ravel(), cv=10)

    # Split test set in feature and target
    x_test = test.iloc[:,0:10].values.astype(float)
    y_test = test.iloc[:,10:11].values.astype(float)

    # Test data
    y_predict = svc.predict(x_test)
    # Get accuracy
    accuracy = accuracy_score(y_test, y_predict)

    # If new accuracy is best than prior
    if accuracy > max_acc:
      # Save Dataset
      pd.DataFrame(test, columns=column).to_excel('test_set_cc.xlsx', index=False)
      pd.DataFrame(train, columns=column).to_excel('train_set_cc.xlsx', index=False)
      # Save Prediction
      prediction = []
      for i in range(0,len(y_predict)):
        prediction.append([y_test[i][0], y_predict[i]])
      pd.DataFrame(prediction, columns=['Test', 'Prediction']).to_excel('prediction_cc.xlsx', index=False)
      # Save model SVC
      pickle.dump(svc, open('svc_cc.pickle', "wb"))
      # Update max accuracy
      max_acc = accuracy 

# Report Metrics for Confidence Classification:
def confidence_classification_report():
  # Import SVC model
  model = pickle.load(open('svc_cc.pickle', 'rb'))

  # Import the test set
  test = pd.read_excel('test_set_cc.xlsx')
  # Split test set in feature and target
  x_test = test.iloc[:,0:10].values.astype(float)
  y_test = test.iloc[:,10:11].values.astype(float)    

  # Test data
  y_predict = model.predict(x_test)
  # Get accuracy
  print(accuracy_score(y_test, y_predict)) 
  # Get report
  print(classification_report(y_test , y_predict, zero_division=1))  
    
# Utility function for Confidence Decision Network
def utility_cdn(x):
  # Maximum utility: 100
  # Minimum utility: -50 (right)
  # Decreases to the left by 50
  return 100 * (x<=0) + 50 * x * (x<=0) - 50 * (x>0)

# Implementation of Confidence Decision Network
def confidence_decision_network():
  # Prefix for the type of node:
  # a : a chance node named ‘a’ (by default)
  # $a : a utility node named ‘a’
  # *a : a decision node named ‘a’
  # Creation Influence Diagram
  id = gum.fastID("Confidence{Notification|Tip|Action}->Forecast{Notification|Tip|Action}->*Decision Confidence{Notification|Tip|Action}->$Utility;Confidence->$Utility;")

  # Import train set
  df = pd.read_excel(io='train_set_cc.xlsx')
      
  # Get Priori Probabilities by counting the number of times that class has occurred
  prior = []
  for x in range(1,4):
    prior.append(len(df[df['Confidence']==x]))
  # Set Normalize Priori Probabilities
  id.cpt('Confidence').fillWith(prior).normalizeAsCPT()

  # Import prediction result
  df = pd.read_excel(io='prediction_cc.xlsx')
  # Get Conditional Probabilities based on SVC test 
  # For each class 
  for x in range(0,3):
    # Get Test/Prediction associated with that class
    test = df[df['Test']==x+1]
    # Inizialise
    tmp = [0, 0, 0]
    # For each class 
    for y in range(0,3):
      # Count number of times that class has been predicted
      tmp[y] = len(test[test['Prediction']==y+1])/10
    # Set Conditional Probabilities
    id.cpt("Forecast")[{"Confidence":x}] = tmp

  # For each real class 
  for real in range(0,3):
    # For each predicted class 
    for pred in range(0,3):
      # Set utility 
      id.utility("Utility")[{"Confidence":real,"Decision Confidence":pred}] = [utility_cdn(pred-real)]

  id.saveBIFXML("id_cdn.bifxml")

# Main for implementation Confidence Decision Network
def main_cdn():
  # Get Dataset for Confidence Classification 
  get_data_cc()

  # Implementation of SVM Multiclass Classification for Confidence
  confidence_classification()
   
  # Report Metrics for Confidence Classification:
  confidence_classification_report()

  # Plot Utility Function
  plot_utility_function(-2, 2, -75, 125, utility_cdn)
  
  # Implementation of Confidence Decision Network
  confidence_decision_network()
  
