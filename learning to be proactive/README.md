# Learning to be Proactive
The project allows participants to play the "*Sequence Memory Game*" with the possibility of asking for assistance when necessary. Before starting to play the game, the participant is shown a tutorial with game instructions on how to get points and request assistance with the option of playing a few trial levels. After the user has agreed to participate, one is asked to first fill out a demographic questionnaire on age, gender, and education level and then the Demographic Game Design questionnaire. Finally, the user begins to play the game with the option to ask for assistance when they need it. The game ends if the user presses the end button or reaches the maximum level. For each user who finished the game, we collected the responses to the questionnaires and the game history, move by move, in a JSON file. 

## Details
- The *_main_.py* file contains the main of the web application developed with Flask, a Python-based module that produces a web application using HTML, CSS and JavaScript. 
- The *templates* folder contains the HTML files, while the *static* folder contains the CSS, JavaScript or image files used. 
- The *json* folder contains the files used to set the language of the application (Italian/English).
- The *.json* files represent sample files of collected player data.

# To install: 
  - pip install flask (versione 2.2.2)
  
# To execute:
  - python main.py   
