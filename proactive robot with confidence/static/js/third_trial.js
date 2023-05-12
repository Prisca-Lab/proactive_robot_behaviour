disabilita_bottoni()
// START GAME
startTrialGame()  

// Returns a shuffled list of items
function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;

    while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;
        temporaryValue = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temporaryValue;
    }

    return array;
}     

function closeButtonClick() {
    indexMatchCard = 0;

    deck1.innerHTML = '';
    deck1.remove()

    deck2.innerHTML = '';
    deck2.remove()

    buttonsRow.innerHTML = '';
    buttonsRow.remove()

    disabilita_bottoni()
    startTrialGame()
}

function createDeck(){
    container[0].appendChild(deck2);

    let difference = symbols.filter(x => sequenceCard.indexOf(x) === -1);
    cards = sequenceCard.filter((ele,pos)=>sequenceCard.indexOf(ele) == pos);
    let length = nCard - nSequence
    if(repetition==1){
        length += 1
    }
    
    for(let i=0; i<length; i++){
        cards.push(difference[i])
    }

    cards = shuffle(cards);

    for (let i=0; i<nCard; i++){
        const li = document.createElement(`li`);
        li.className = `card open show`;
        const inner = document.createElement(`i`);
        inner.className = `fa fa-${cards[i]}`;
        deck2.appendChild(li);
        li.appendChild(inner);
        li.addEventListener(`click`, processClick);
    }
    
    container[0].appendChild(buttonsRow);
    img.style.display="block";
    jsTextBlock.style.display="block";
    set_image(img)

    buttonsRow.appendChild(img)
    buttonsRow.appendChild(jsTextBlock)
    buttonsRow.appendChild(betaButton1)
    buttonsRow.appendChild(betaButton2);
    buttonsRow.appendChild(betaButton3);
    buttonsRow.appendChild(betaButton4)
    buttonsRow.appendChild(endButtonTrial)

    text_chat.innerHTML = ''
    text_chat.innerHTML = language_json.trial.bubbleText[0]
    yesButton.style.display="none";
    noButton.style.display="none";
    // Random Help
    timerRandom = randomIntFromInterval(2000,7000)
    timeoutHelp = setTimeout(function(){return random_sugg()}, timerRandom)
}

function abilita_bottoni(){
    for (let i in buttons_array) {
        buttons_array[i].disabled = false
        buttons_array[i].className = "suggerimenti_abilitati" 
    }
}

function disabilita_bottoni(){
    for (let i in buttons_array) {
        buttons_array[i].disabled = true
        buttons_array[i].className = "suggerimenti_disabilitati" 
    }
}

function timing(){
    seconds += 1
    if(seconds == 60){
        seconds = 0
        minutes += 1
    }
    myText.innerHTML = language_json.trial.description[0] + level + ' \u00A0 \u00A0 \u00A0 ' + language_json.trial.description[1] + score + ' \u00A0 \u00A0 \u00A0 ' + language_json.trial.description[2] + minutes + ":" + seconds ;
    timeout = setTimeout(function(){timing()}, 1000);
}

function getRealCard(){
    let li = deck1.childNodes;
    let inner = li[indexMatchCard].childNodes;
    let symbol = inner[0].className;
    // remove the 'fa fa-'
    realCard = symbol.slice(6);
}

function popupFunction(score, color){
    popup.innerHTML = score
    popup.className = `popuptext show`;
    popup.style.backgroundColor = color
    
    setTimeout(function(){
        popup.innerHTML = ''
        popup.className = `popuptext hide`;}, 800
    );
}

function processClick() {
    if(this.className == `card open show` && indexMatchCard!=nSequence && random_how==-1){
        clearTimeout(timeoutHelp)
        //Reset bubble
        text_chat.innerHTML = ''
        bubbleText = 0
        text_chat.innerHTML = language_json.trial.bubbleText[0]
        disabilita_bottoni()
        
        getSelectedCard(this);
        getRealCard()  
        if(realCard === selectedCard){
            popupFunction('+ 10', '#27f198')
            lockMatch(deck1.childNodes[indexMatchCard])
            matchCard.push(realCard)

            score += 10
            indexMatchCard += 1;
    
            for (let i=0; i<hideCards.length; i++){
                displayCard(deck2.childNodes[hideCards[i]])
            }
            hideCards = []
            hideCardsItem = []

            if(indexMatchCard==nSequence){    
                clearTimeout(timeout)
 
                setTimeout(function(){
                    if(level==1){
                        let tr = document.createElement("tr")
                        let td = document.createElement("td")
                        td.innerHTML = ''
                        tr.appendChild(td)
    
                        td = document.createElement("td")
                        td.innerHTML = language_json.trial.table[0]
                        tr.appendChild(td)
    
                        td = document.createElement("td")
                        td.innerHTML = language_json.trial.table[1]
                        tr.appendChild(td)
                        table.appendChild(tr)
                        
                        tr = document.createElement("tr")
                        td = document.createElement("td")
                        td.innerHTML = 1
                        tr.appendChild(td)
                        
                        td = document.createElement("td")
                        tr.classList.add("selected");
                        td.innerHTML = language_json.trial.table[2]
                        tr.appendChild(td)
    
                        td = document.createElement("td")
                        td.id = "trial_table"
                        td.innerHTML = score
                        tr.appendChild(td)
                        table.appendChild(tr)
                    }else{
                        let td = document.getElementById("trial_table")
                        td.innerHTML = score
                    }

                    if(level >= maxLevelTrial){
                        document.getElementById("next").style.display = "none"
                    }

                    buttonModal.click()
                }, 1000);  
            }else{
                timerRandom = randomIntFromInterval(2000,7000)
                timeoutHelp = setTimeout(function(){return random_sugg()}, timerRandom)
            }
        } else {
            popupFunction('- 5', '#cf2c2c')
            score -= 5

            wrongCards.push(this)
            wrongSelection(this)

            setTimeout(function(){
                for (let i=0; i<wrongCards.length; i++){
                    displayCard(wrongCards[i])
                    wrongCards.pop(this)
                }
            }, 100);
            timerRandom = randomIntFromInterval(2000,7000)
            timeoutHelp = setTimeout(function(){return random_sugg()}, timerRandom)
        }
        myText.innerHTML = language_json.trial.description[0] + level + ' \u00A0 \u00A0 \u00A0 ' + language_json.trial.description[1] + score + ' \u00A0 \u00A0 \u00A0 ' + language_json.trial.description[2] + minutes + ":" + seconds ;
    }
}

function lockMatch(item) {
    item.className = `card match`;
}

function wrongSelection(item) {
    item.className  = `card open show wrong`;
}

// Show the card by adding 'open' and 'show' class name
function displayCard(item) {
    item.className = `card open show`;
}

function hideCard(item) {
    item.className = `card hide`;
}

// Hide opened cards by removing the 'open' and 'show' class name
function removeAllCards() {
    let openClass = document.getElementsByClassName(`open`);
    while (openClass.length){
        openClass[0].className = `card`;
    }
}

function getSelectedCard(item) {
    let symbol = item.childNodes[0].className;
    // remove the 'fa fa-'
    selectedCard = symbol.slice(6);
}

function setTrial(){
    level += 1

    if(level == 1){ 
        nSequence = nSequence + 1
        repetition = 0
    }else if(level == 2){ 
        nCard = nCard + 1
        repetition = 0 
    }else{
        repetition = 1
    }
}

function abilita_bottone(btn){
    btn.disabled = false
    btn.className = "suggerimenti_abilitati" 
}

function disabilita_bottone(btn){
    btn.disabled = true
    btn.className = "suggerimenti_disabilitati" 
}

function randomIntFromInterval(min, max) { // min and max included 
    return Math.floor(Math.random() * (max - min + 1) + min)
}

function startTrialGame(){
    if(level >= maxLevelTrial){
        endButtonTrial.click()
    }
    else{
        container[0].appendChild(deck1);

        let shuffledDeck = shuffle(symbols);
        sequenceCard = [];
        matchCard = [];
    
        setTrial()
        timing()
    
        if(repetition==1){
            shuffledDeck = shuffledDeck.slice(0, nSequence-1)
            shuffledDeck.push(shuffledDeck[Math.floor(Math.random() * shuffledDeck.length)])
            shuffledDeck = shuffle(shuffledDeck);
        }
    
        for (let i=0; i<nSequence; i++){
            const li = document.createElement(`li`);
            li.className = `card open show`;
            const inner = document.createElement(`i`);
            sequenceCard.push(shuffledDeck[i])
            inner.className = `fa fa-${shuffledDeck[i]}`;
            deck1.appendChild(li);
            li.appendChild(inner);
        }
     
        setTimeout(function(){
            return removeAllCards(), createDeck();}, 5000
        );
    } 
}

betaButton2.addEventListener("click", function() {
    disabilita_bottoni()
    if(indexMatchCard!=nSequence){
        getRealCard() 
        const index = cards.findIndex(object => {
            return object === realCard;
        });
        
        var selection = cards.filter(x => hideCardsItem.indexOf(x) === -1);
        let middle_name = selection[parseInt(selection.length/2)]
        let middle = cards.findIndex(object => {
            return object === middle_name;
        });
        selection = selection.filter(x => x != realCard);

        if(selection.length != 0){ 
            // PARI
            if((selection.length+1)%2 == 0){
                for(let i=0; i<selection.length; i++){
                    var tmp = cards.findIndex(object => {
                        return object === selection[i];
                    });
                    if(index >= middle && tmp < middle){
                        hideCard(deck2.childNodes[tmp])
                        hideCards.push(tmp)
                        hideCardsItem.push(selection[i])
                    }else if(index < middle && tmp >= middle){
                        hideCard(deck2.childNodes[tmp])
                        hideCards.push(tmp)
                        hideCardsItem.push(selection[i])
                    }
                }
            }else{
                for(let i=0; i<selection.length; i++){
                    var tmp = cards.findIndex(object => {
                        return object === selection[i];
                    });
                    if(index == middle && tmp < middle){
                        hideCard(deck2.childNodes[tmp])
                        hideCards.push(tmp)
                        hideCardsItem.push(selection[i])
                    }else if(index > middle && tmp < middle){
                        hideCard(deck2.childNodes[tmp])
                        hideCards.push(tmp)
                        hideCardsItem.push(selection[i])
                    }else if(index < middle && tmp > middle){
                        hideCard(deck2.childNodes[tmp])
                        hideCards.push(tmp)
                        hideCardsItem.push(selection[i])
                    }
                }
            }

            popupFunction('- 2', '#0c96ff')
            score -= 2
        }       
    }
    //Reset bubble
    if(random_how!=2){
        yesButton.style.display="none";
        noButton.style.display="none";
        text_chat.innerHTML = ''
        bubbleText = 0
        text_chat.innerHTML = language_json.trial.bubbleText[0]
        disabilita_bottoni()
    }
});

betaButton1.addEventListener("click", function() {
    disabilita_bottoni()
    if(indexMatchCard!=nSequence){
        getRealCard() 
        var selection = cards.filter(x => x != realCard);
        selection = selection.filter(x => hideCardsItem.indexOf(x) === -1);

        if(selection.length != 0){
            popupFunction('- 1', '#0c96ff')
            score -= 1

            var item = selection[Math.floor(Math.random()*selection.length)];
            const index = cards.findIndex(object => {
                return object === item;
            });

            hideCard(deck2.childNodes[index])
            hideCards.push(index)
            hideCardsItem.push(item)
        }
    }
    //Reset bubble
    if(random_how!=2){
        yesButton.style.display="none";
        noButton.style.display="none";
        text_chat.innerHTML = ''
        bubbleText = 0
        text_chat.innerHTML = language_json.trial.bubbleText[0] 
        disabilita_bottoni()
    }
});

betaButton3.addEventListener("click", function() {
    disabilita_bottoni()
    if(indexMatchCard!=nSequence){
        getRealCard() 
        var selection = cards.filter(x => x != realCard);
        selection = selection.filter(x => hideCardsItem.indexOf(x) === -1);

        if(selection.length != 0){
            for(let i=0; i<selection.length; i++){
                var tmp = cards.findIndex(object => {
                    return object === selection[i];
                });
                hideCard(deck2.childNodes[tmp])
                hideCards.push(tmp)
                hideCardsItem.push(selection[i])
            }
                
            popupFunction('- 3', '#0c96ff')
            score -= 3
        }
    }
    //Reset bubble
    if(random_how!=2){
        yesButton.style.display="none";
        noButton.style.display="none";
        text_chat.innerHTML = ''
        bubbleText = 0
        text_chat.innerHTML = language_json.trial.bubbleText[0]
        disabilita_bottoni()
    }
});

betaButton4.addEventListener("click", function() {
    disabilita_bottoni()
    if(indexMatchCard!=nSequence){
        popupFunction('- 4', '#0c96ff')
        score -= 4

        removeAllCards()
        let hideClass = document.getElementsByClassName(`card hide`);
        while (hideClass.length){
            hideClass[0].className = `card`;
        }

        for (let i=0; i<nSequence; i++){
            if(deck1.childNodes[i].className == `card`){
                displayCard(deck1.childNodes[i])
            }
        }

        setTimeout(function(){
            removeAllCards()

            for (let i=0; i<hideCards.length; i++){
                hideCard(deck2.childNodes[hideCards[i]])
            }

            for (let i=0; i<nCard; i++){
                if(deck2.childNodes[i].className == `card`){
                    displayCard(deck2.childNodes[i])
                }
            }
            //Reset bubble
            if(random_how!=2){
                yesButton.style.display="none";
                noButton.style.display="none";
                text_chat.innerHTML = ''
                bubbleText = 0
                text_chat.innerHTML = language_json.trial.bubbleText[0]
                disabilita_bottoni()
            }
        }, 5000);
    }
});


function random_sugg(){
    var selection = cards.filter(x => x != realCard);
    selection = selection.filter(x => hideCardsItem.indexOf(x) === -1);

    if(selection.length != 0){
        random_how = Math.floor(Math.random() * 3);
        yesButton.style.display="none";
        noButton.style.display="none";
        if(random_how==0){
        /* --------- Notification -------------
            System: "Penso che ti possa servire un aiuto!" e sblocca gli aiuti
            User: decide se e quale aiuto scegliere 
        */
            text_chat.innerHTML = ''
            bubbleText = 1
            text_chat.innerHTML = language_json.trial.bubbleText[1]
            
            /* FURHAT */
            let decision_net = {}
            decision_net['Testo'] = language_json.trial.bubbleText[1]
            $.ajax({
                url:"/furhat_say",
                type:"POST",
                contentType: "application/json",
                data: JSON.stringify(JSON.stringify(decision_net)),
                success: function(result) {
                    //Da togliere
                    console.log("Result:");
                    console.log(result);
                }
            });
            
            abilita_bottoni()
            random_how = -1 
        }else if(random_how==1){
        /* --------- Suggestion -------------
        System: "Ti suggerisco di utilizzare questo aiuto" e sblocca quell'aiuto
            User: decide se utilizzare l'aiuto
        */
            // Selezione random suggerimento
            suggAbilitato = sugg[Math.floor(Math.random()*sugg.length)];
            const index = sugg.findIndex(object => {
                return object === suggAbilitato;
            });

            text_chat.innerHTML = ''
            bubbleText = 2
            text_chat.innerHTML = language_json.trial.bubbleText[2] + language_json.trial.suggName[index] +'!';
            abilita_bottone(document.getElementById(suggAbilitato))
            var disab = sugg.filter(x => x != suggAbilitato);
            for (let i=0; i<disab.length; i++){
                disabilita_bottone(document.getElementById(disab[i]))
            }    
            random_how = -1
        }else if(random_how==2){
        /* --------- Intervention -------------
            System: "Ho scelto di utilizzare l'aiuto X" e attiva quell'aiuto
            User: non decide ma indica se ha gradito l'aiuto oppure no
        */
            // Selezione random suggerimento
            suggAbilitato = sugg[Math.floor(Math.random()*sugg.length)];
            const index = sugg.findIndex(object => {
                return object === suggAbilitato;
            });
            abilita_bottone(document.getElementById(suggAbilitato))
            var disab = sugg.filter(x => x != suggAbilitato);
            for (let i=0; i<disab.length; i++){
                disabilita_bottone(document.getElementById(disab[i]))
            } 
        
            text_chat.innerHTML = ''
            bubbleText = 3
            text_chat.innerHTML = language_json.trial.bubbleText[3] + language_json.trial.suggName[index] + language_json.trial.bubbleText[4];
            document.getElementById(suggAbilitato).click()
            yesButton.style.display="block";
            noButton.style.display="block";
        }
    }
}

