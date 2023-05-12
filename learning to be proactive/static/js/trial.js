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
    set_image(img)

    buttonsRow.appendChild(img)
    buttonsRow.appendChild(betaButton1)
    buttonsRow.appendChild(betaButton2);
    buttonsRow.appendChild(betaButton3);
    buttonsRow.appendChild(betaButton4)
    buttonsRow.appendChild(endButtonTrial)
}

function abilita_bottoni(){
    betaButton1.disabled = false
    betaButton1.className = "suggerimenti_abilitati"

    betaButton2.disabled = false
    betaButton2.className = "suggerimenti_abilitati"

    betaButton3.disabled = false
    betaButton3.className = "suggerimenti_abilitati"

    betaButton4.disabled = false
    betaButton4.className = "suggerimenti_abilitati"
}

function disabilita_bottoni(){
    betaButton1.disabled = true
    betaButton1.className = "suggerimenti_disabilitati"

    betaButton2.disabled = true
    betaButton2.className = "suggerimenti_disabilitati"

    betaButton3.disabled = true
    betaButton3.className = "suggerimenti_disabilitati"

    betaButton4.disabled = true
    betaButton4.className = "suggerimenti_disabilitati"
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
    if(this.className == `card open show` && indexMatchCard!=nSequence){
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
    abilita_bottoni()
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
    abilita_bottoni()
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
    abilita_bottoni()
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

            abilita_bottoni()
        }, 5000);
    }
});
