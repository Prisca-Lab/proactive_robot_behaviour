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

# Get inference from ID without evidence
# Input: ID path, nome of png file 
def get_inference_without_evs(import_path, export_path):
  # Load ID
  id = gum.loadID(import_path)

  # Create inference
  ie = gum.ShaferShenoyLIMIDInference(id)
  # Make inference
  ie.makeInference()
  # Export inference in .png
  gumimage.exportInference(id, export_path)

  # If notebook imported
  # import pyAgrum.lib.notebook as gnb
  # gnb.showInference(id)
  
# Example of Decision System Implementation
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

    random.seed(random.random())
    confidence = random.choice(['Notification', 'Tip', 'Action'])
    return assistance, time, confidence
  else:
    return assistance

##################################################################################################

# Get Dataset for Assistance Requested Classification 
def get_data_arc():
    # Action
    # Nessuna: None, Corrispondenza: Match, Errore: Mistake, Aiuto: Assistance
    dict_a = {
        'Nessuna':0, 
        'Corrispondenza':1, 
        'Errore':2, 
        'Aiuto':3}
    # Assistance Requested 
    # Nessuna: None, Nascondi Carta: Hide Card, Suggerisci Posizione: Suggest Position, 
    # Indica Posizione: Indicate Position, Rivedi Sequenza: Review Sequence
    dict_ar = {
        'Nessuna':0, 
        'NascondiCarta(suggerimento)':1, 
        'SuggerisciPosizione(suggerimento)':2, 
        'IndicaPosizione(suggerimento)':3, 
        'RivediSequenza(suggerimento)':4}
    set_assistance = [
        'NascondiCarta(suggerimento)', 
        'SuggerisciPosizione(suggerimento)', 
        'IndicaPosizione(suggerimento)', 
        'RivediSequenza(suggerimento)']
    write = []
    for txt_path in Path("./data/").glob("*.json"):
        # Get data from file
        file_json = open(txt_path)
        data = json.load(file_json)
        # If they have reached at least level 6 (the first with 6 cards of the sequence to remember)
        if (data["partita"]["livello_raggiunto"]>6):
            # Get DGD's result of each player type
            dgd = get_dgd_result(data["dgd_test"])
            dict_level = data["partita"]["livello"]
            # For each level 
            for level_loop in range(1, len(dict_level)+1):
                level = str(level_loop)
                if(level in dict_level.keys()): 
                    # Set number of cards of sequence to remember
                    n_sequence = dict_level[level]["n_sequenza"] 
                    # If the level has at least 6 cards to remember
                    if(n_sequence>5):
                        # Reset Old Action 
                        old_action = ''
                        # For each state
                        dict_state = dict_level[level]["sequenza"]
                        for state_ in range(0, len(dict_state.keys())):
                            state = str(state_)
                            # Set number of deck cards to choose from
                            n_deck_cards = dict_level[level]["n_carte"]
                            moves_dict = dict_state[state]["mossa"]
                            # For each action
                            for move_loop in range(0, len(moves_dict)):
                                move = str(move_loop)
                                # Set Assistance Requested
                                value_request = None
                                action_type = moves_dict[move]["tipo"]
                                if action_type in set_assistance:
                                    value_request = dict_ar[action_type]
                                elif action_type == 'Corrispondenza' or action_type == 'Errore':
                                    value_request = dict_ar['Nessuna']

                                if(value_request!=None):
                                    # Set Prior Action
                                    if(old_action in set_assistance):
                                        val_old_action = dict_a['Aiuto']
                                    elif(old_action=='Errore' or old_action=='Corrispondenza'):
                                        val_old_action = dict_a[old_action]
                                    else:
                                        val_old_action = dict_a['Nessuna']
                                    # Write the row on array
                                    write.append([dgd["Conqueror"], dgd["Manager"], dgd["Wanderer"], dgd["Participant"], n_sequence, state_+1, n_deck_cards, val_old_action, value_request])
    
                                # Update Old Action with the new one 
                                old_action = action_type

                                # If the move is one the assistances that changes the number of deck cards
                                if action_type in set_assistance[:3]:
                                    # Update number of deck cards
                                    n_deck_cards = moves_dict[move]["nCarte_nonNascoste_dopo"]
    
    # Convert array to Pandas DataFrame
    df = pd.DataFrame(write, columns = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested"])
    # Drop Duplicates
    df.drop_duplicates(subset=None, inplace=True)
    # Write data into file CSV
    df.to_csv('dataset_arc.csv', index=False, sep=",")

# Update Dataset for Assistance Requested Classification 
def update_data_arc(data):
  # Define target name
  y = 'AssistanceRequested'
  # Split the dataset by class
  # Class None
  df0 = data[data[y]==0].sample(frac=1, random_state=None)
  # Class Hide Card
  df1 = data[data[y]==1].sample(frac=1, random_state=None)
  # Class Suggest Position
  df2 = data[data[y]==2].sample(frac=1, random_state=None)
  # Class Indicate Position
  df3 = data[data[y]==3].sample(frac=1, random_state=None)
  # Class Review Sequence
  df4 = data[data[y]==4].sample(frac=1, random_state=None)
  # 1. Extract Test Set: 10 elements of each class
  df_test = pd.concat([df0[:10], df1[:10], df2[:10], df3[:10], df4[:10]]).sample(frac=1)

  # 2. Reduction of Majority class
  reduct_df0 = df0[10:].sample(n=270, random_state=None)
  # Update Train Set
  df_train = pd.concat([reduct_df0, df1[10:], df2[10:], df3[10:], df4[10:]]).sample(frac=1) 
  x_train = df_train.iloc[:,0:8].values.astype(float)
  y_train = df_train.iloc[:,8:9].values.astype(float)

  # 3. Synthetic Minority Oversampling Technique
  sm = SMOTE(sampling_strategy={0:270, 1:250, 2:255, 3:260, 4:265},random_state=None)
  x_res, y_res = sm.fit_resample(x_train, y_train)
  df_tempX = pd.DataFrame(x_res, columns=["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction"])
  df_tempY = pd.DataFrame(y_res, columns=["AssistanceRequested"])
  df_train = df_tempX.assign(AssistanceRequested = lambda x: df_tempY["AssistanceRequested"])

  return df_train, df_test

# SVM Multiclass Classification for Assistance Requested
def assistance_classification():
  # Import the dataset
  dataset = pd.read_csv('dataset_arc.csv',delimiter= ',')

  column = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested"]
  max_acc = 0
  # Repeat the process to get the best accuracy
  for i in range(0,200):
    # Get updated train and test set
    train, test= update_data_arc(dataset)
    # Split train set in feature and target
    x_train = train.iloc[:,0:8].values.astype(float)
    y_train = train.iloc[:,8:9].values.astype(float)

    # Define SVC
    svc = make_pipeline(StandardScaler(), SVC(gamma='auto', probability=True))
    # Fit data to StandardScaler
    svc.fit(x_train, y_train.ravel())
    # Cross-validation on train set
    cross_val_score(svc, x_train, y_train.ravel(), cv=10)

    # Split test set in feature and target
    x_test = test.iloc[:,0:8].values.astype(float)
    y_test = test.iloc[:,8:9].values.astype(float)
    # Test data
    y_predict = svc.predict(x_test)
    # Get accuracy
    accuracy = accuracy_score(y_test, y_predict)

    # If new accuracy is best than prior
    if accuracy > max_acc:
      # Save Dataset
      pd.DataFrame(test, columns=column).to_excel('test_set_arc.xlsx', index=False)
      pd.DataFrame(train, columns=column).to_excel('train_set_arc.xlsx', index=False)
      # Save Prediction
      prediction = []
      for i in range(0,len(y_predict)):
        prediction.append([y_test[i][0], y_predict[i]])
      pd.DataFrame(prediction,  columns=['Test', 'Prediction']).to_excel('prediction_arc.xlsx', index=False)
      # Save model SVC
      pickle.dump(svc, open('svc_arc.pickle', "wb"))
      # Update max accuracy
      max_acc = accuracy 

# Report Metrics for Assistance Requested Classification:
def assistance_classification_report():
  # Import SVC model
  model = pickle.load(open('svc_arc.pickle', 'rb'))

  # Import the test set
  test = pd.read_excel('test_set_arc.xlsx')
  # Split test set in feature and target
  x_test = test.iloc[:,0:8].values.astype(float)
  y_test = test.iloc[:,8:9].values.astype(float)    

  # Test data
  y_predict = model.predict(x_test)
  # Get accuracy
  print(accuracy_score(y_test, y_predict)) 
  # Get report
  print(classification_report(y_test , y_predict, zero_division=1))

# Utility function for Assistance Decision Network
def utility_adn(x):
    # Maximum utility: 60
    # Decreases faster to the right by 15
    # Decreases less quickly to the left by 10
    return 60 * (x<=0) + 10 * x * (x<=0) - 15 * x * (x>0) + 60 * (x>0)

# Implementation of Assistance Decision Network
def assistance_decision_network():
  # Prefix for the type of node:
  # a : a chance node named ‘a’ (by default)
  # $a : a utility node named ‘a’
  # *a : a decision node named ‘a’
  # Creation Influence Diagram
  id = gum.fastID("Assistance Requested{None|Hide Card|Suggest Position|Indicate Position|Review Sequence}->Forecast{None|Hide Card|Suggest Position|Indicate Position|Review Sequence}->*Decision Assistance{None|Hide Card|Suggest Position|Indicate Position|Review Sequence}->$Utility;Assistance Requested->$Utility;")
  
  # Import train set
  df = pd.read_excel(io='train_set_arc.xlsx')
      
  # Get Priori Probabilities by counting the number of times that event (or class) has occurred
  ''' 
  Dict Assistance Requested= {
      'None':0, 
      'Hide Card':1, 
      'Suggest Position':2, 
      'Indicate Position':3, 
      'Review Sequence':4}
  '''
  prior = []
  for x in range(0,5):
    prior.append(len(df[df['AssistanceRequested']==x]))
  # Set Normalize Priori Probabilities
  id.cpt('Assistance Requested').fillWith(prior).normalizeAsCPT()

  # Import prediction result
  df = pd.read_excel(io='prediction_arc.xlsx')
  # Get Conditional Probabilities based on SVC test 
  # For each class 
  for x in range(0,5):
    # Get Test/Prediction associated with that class
    test = df[df['Test']==x]
    # Inizialise
    tmp = [0, 0, 0, 0, 0]
    # For each class 
    for y in range(0,5):
      # Count number of times that class has been predicted
      tmp[y] = len(test[test['Prediction']==y])/10
    # Set Conditional Probabilities
    id.cpt("Forecast")[{"Assistance Requested":x}] = tmp

  # For each real class 
  for real in range(0,5):
    # For each predicted class 
    for pred in range(0,5):
      # Set utility 
      id.utility("Utility")[{"Assistance Requested":real,"Decision Assistance":pred}] = [utility_adn(pred-real)]
          
  id.saveBIFXML("id_adn.bifxml")

# Main for implementation Assistance Decision Network
def main_adn():
  # Get Dataset for Assistance Requested Classification 
  get_data_arc()

  # Implementation of SVM Multiclass Classification for Assistance Requested
  assistance_classification()

  # Report Metrics for Assistance Requested Classification:
  assistance_classification_report()

  # Plot Utility Function
  plot_utility_function(-4, 4, -10, 70, utility_adn)

  # Implementation of Assistance Decision Network
  assistance_decision_network()

##################################################################################################

# Get Dataset for Request Time Classification 
def get_data_rtc():
  # Action
  # Nessuna: None, Corrispondenza: Match, Errore: Mistake, Aiuto: Assistance
  dict_a = {
    'Nessuna':0, 
    'Corrispondenza':1, 
    'Errore':2, 
    'Aiuto':3}
  # Assistance Requested 
  # Nessuna: None, Nascondi Carta: Hide Card, Suggerisci Posizione: Suggest Position, 
  # Indica Posizione: Indicate Position, Rivedi Sequenza: Review Sequence
  dict_ar = {
    'Nessuna':0, 
    'NascondiCarta(suggerimento)':1, 
    'SuggerisciPosizione(suggerimento)':2, 
    'IndicaPosizione(suggerimento)':3, 
    'RivediSequenza(suggerimento)':4}
  set_assistance = [
    'NascondiCarta(suggerimento)', 
    'SuggerisciPosizione(suggerimento)', 
    'IndicaPosizione(suggerimento)', 
    'RivediSequenza(suggerimento)']
  write = []
  for txt_path in Path("./data/").glob("*.json"):
    # Get data from file
    file_json = open(txt_path)
    data = json.load(file_json)
    # If they have reached at least level 6 (the first with 6 cards of the sequence to remember)
    if (data["partita"]["livello_raggiunto"]>6):
      # Get DGD's result of each player type
      dgd = get_dgd_result(data["dgd_test"])
      dict_level = data["partita"]["livello"]
      # For each level 
      for level_loop in range(1, len(dict_level)+1):
        level = str(level_loop)
        if(level in dict_level.keys()): 
          # Set number of cards of sequence to remember
          n_sequence = dict_level[level]["n_sequenza"] 
          # If the level has at least 6 cards to remember
          if(n_sequence>5):
            # Reset Old Action 
            old_action = ''
            # Reset Old Time with start time
            old_time = dict_level[level]["orario_inizio"]
            # For each state
            dict_state = dict_level[level]["sequenza"]
            for state_ in range(0, len(dict_state.keys())):
              state = str(state_)
              # Set number of deck cards to choose from
              n_deck_cards = dict_level[level]["n_carte"]
              moves_dict = dict_state[state]["mossa"]
              # For each action
              for move_loop in range(0, len(moves_dict)):
                move = str(move_loop)
                # Set Assistance Requested
                value_request = None
                action_type = moves_dict[move]["tipo"]
                if action_type in set_assistance:
                  value_request = dict_ar[action_type]

                # Set Time
                new_time = str(moves_dict[move]["orario"])

                if(value_request!=None):
                  # Set Prior Action
                  if(old_action in set_assistance):
                    val_old_action = dict_a['Aiuto']
                  elif(old_action=='Errore'):
                    val_old_action = dict_a[old_action]
                  elif(old_action=='Corrispondenza'):
                    val_old_action = dict_a[old_action]
                  else:
                    val_old_action = dict_a['Nessuna']

                  # Convert to datetime object
                  start_time = datetime.strptime(old_time,"%H:%M:%S:%f")
                  # Convert to datetime object
                  end_time = datetime.strptime(new_time,"%H:%M:%S:%f")
                  # Calculate Request Time
                  request_time = (end_time - start_time).total_seconds()
                  # Find bin of time for inclusion
                  bin_time = math.trunc(request_time)
                  write.append([dgd["Conqueror"], dgd["Manager"], dgd["Wanderer"], dgd["Participant"], n_sequence, state_+1, n_deck_cards, val_old_action, value_request, bin_time, request_time])
                
                # Update Old Action with the new one 
                old_action = action_type
                # Update Old Time with the new one 
                old_time = new_time

                # If the move is one the assistances that changes the number of deck cards
                if action_type in set_assistance[:3]:
                  # Update number of deck cards
                  n_deck_cards = moves_dict[move]["nCarte_nonNascoste_dopo"]
  
  # Convert array to Pandas DataFrame  
  df = pd.DataFrame(write, columns = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested", "Bin", "Time"])
  # Drop Duplicates
  df.drop_duplicates(subset=None, inplace=True)
  # Write data into file CSV
  df.to_csv('dataset_rtc.csv', index=False, sep=",")

# Update Dataset for Request Time Classification 
def update_data_rtc(data):
  # Define target name
  y = 'Bin'
  # Split the dataset by class
  # Reduction of Class [2,3)
  df2 = data[data[y]==2].sample(n=99, random_state=None)
  # Reduction of Class [3,4)
  df3 = data[data[y]==3].sample(n=94, random_state=None)
  # Class [4,5]
  df4 = data[data[y]==4].sample(frac=1, random_state=None)

  # Extract Test Set: 10 elements of each class
  df_test = pd.concat([df2[:10], df3[:10], df4[:10]]).sample(frac=1)

  # Extract Train Set
  df_train = pd.concat([df2[10:], df3[10:], df4[10:]]).sample(frac=1) 

  return df_train, df_test

# SVM Multiclass Classification for Request Time
def time_classification():
  # Import the dataset
  dataset = pd.read_csv('dataset_rtc.csv',delimiter= ',')

  column = ["Conqueror", "Manager", "Wanderer", "Participant", "Sequence", "State", "Deck", "PriorAction", "AssistanceRequested", "Bin", "Time"]
  max_acc = 0
  # Repeat the process to get the best accuracy
  for i in range(0,200):
    # Get updated train and test set
    train, test= update_data_rtc(dataset)
    # Split train set in feature and target (bin)
    x_train = train.iloc[:,0:9].values.astype(float)
    y_train = train.iloc[:,9:10].values.astype(float)

    # Define SVC
    svc = make_pipeline(StandardScaler(), SVC(gamma='auto', probability=True))
    # Fit data to StandardScaler
    svc.fit(x_train, y_train.ravel())
    # Cross-validation on train set
    cross_val_score(svc, x_train, y_train.ravel(), cv=10)

    # Split test set in feature and target
    x_test = test.iloc[:,0:9].values.astype(float)
    y_test = test.iloc[:,9:10].values.astype(float)
    # Time value
    z_test = test.iloc[:,10:11].values.astype(float)

    # Test data
    y_predict = svc.predict(x_test)
    # Get accuracy
    accuracy = accuracy_score(y_test, y_predict)

    # If new accuracy is best than prior
    if accuracy > max_acc:
      # Save Dataset
      pd.DataFrame(test, columns=column).to_excel('test_set_rtc.xlsx', index=False)
      pd.DataFrame(train, columns=column).to_excel('train_set_rtc.xlsx', index=False)
      # Save Prediction
      prediction = []
      for i in range(0,len(y_predict)):
        prediction.append([z_test[i][0], y_test[i][0], y_predict[i]])
      pd.DataFrame(prediction, columns=['Time', 'Test', 'Prediction']).to_excel('prediction_rtc.xlsx', index=False)
      # Save model SVC
      pickle.dump(svc, open('svc_rtc.pickle', "wb"))
      # Update max accuracy
      max_acc = accuracy 

# Report Metrics for Request Time Classification:
def time_classification_report():
  # Import SVC model
  model = pickle.load(open('svc_rtc.pickle', 'rb'))

  # Import the test set
  test = pd.read_excel('test_set_rtc.xlsx')
  # Split test set in feature and target
  x_test = test.iloc[:,0:9].values.astype(float)
  y_test = test.iloc[:,9:10].values.astype(float)    

  # Test data
  y_predict = model.predict(x_test)
  # Get accuracy
  print(accuracy_score(y_test, y_predict)) 
  # Get report
  print(classification_report(y_test , y_predict, zero_division=1))

# Utility function for Time Decision Network
def utility_tdn(x):
    # Maximum utility: 10
    # Minimum utility: -50 (right)
    # Decreases to the left by 50
    return 100 * (x<=0) + 50 * x * (x<=0) - 50 * (x>0)

# Implementation of Time Decision Network
def time_decision_network():
  # Prefix for the type of node:
  # a : a chance node named ‘a’ (by default)
  # $a : a utility node named ‘a’
  # *a : a decision node named ‘a’
  # Creation Influence Diagram
  id = gum.fastID("Request Time[2,3,4,5]->Forecast[2,3,4,5]->*Decision Time[2,3,4,5]->$Utility;Request Time->$Utility;")

  # Import train set
  df = pd.read_excel(io='train_set_rtc.xlsx')
      
  # Get Priori Probabilities by counting the number of times that class has occurred
  prior = []
  for x in range(2,5):
    prior.append(len(df[df['Bin']==x]))
  # Set Normalize Priori Probabilities
  id.cpt('Request Time').fillWith(prior).normalizeAsCPT()

  # Import prediction result
  df = pd.read_excel(io='prediction_rtc.xlsx')
  # Get Conditional Probabilities based on SVC test 
  # For each class value (2,5)
  for x in range(0,3):
    # Get Test/Prediction associated with that class
    test = df[df['Test']==x+2]
    # Inizialise
    tmp = [0, 0, 0]
    # For each class 
    for y in range(0,3):
      # Count number of times that class has been predicted
      tmp[y] = len(test[test['Prediction']==y+2])/10
    # Set Conditional Probabilities
    id.cpt("Forecast")[{"Request Time":x}] = tmp

  # For each real class 
  for real in range(0,3):
    # For each predicted class 
    for pred in range(0,3):
      # Set utility 
      id.utility("Utility")[{"Request Time":real,"Decision Time":pred}] = [utility_tdn(pred-real)]
   
  id.saveBIFXML("id_tdn.bifxml")

# Main for implementation Time Decision Network
def main_tdn():
  # Get Dataset for Request Time Classification 
  get_data_rtc()

  # Implementation of SVM Multiclass Classification for Request Time
  time_classification()

  # Report Metrics for Request Time Classification:
  time_classification_report()

  # Plot Utility Function
  plot_utility_function(-2, 2, -75, 125, utility_tdn)

  # Implementation of Time Decision Network
  time_decision_network()

##################################################################################################
