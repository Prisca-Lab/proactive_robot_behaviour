disabilita_bottoni()
// START GAME
submitForm()
startGame() 

function submitForm(){
    file["eta"] = data["age"]
    file["genere"] = data["gender"] 
    file["formazione"] = data["education"] 
    file["dgd_test"] = dgd_test
    file["score_ranking"] = players
    file["partita"] = {}
    file["partita"]["livello_max"] = maxLevel
    file["partita"]["livello"] = {}
}

function closeButtonClick() {
    table.innerHTML = '' 

    nWrongLevel = 0
    nHelpLevel = 0
    scoreLevel = 0
    indexMatchCard = 0;

    deck1.innerHTML = '';
    deck1.remove()

    deck2.innerHTML = '';
    deck2.remove()

    buttonsRow.innerHTML = '';
    buttonsRow.remove()

    disabilita_bottoni()
    setTimeout(function(){
        return startGame();}, 800
    );
}

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

function setGame(){
    level += 1

    if(level <= 12){
        if(level%3 == 1){ 
            nSequence = nSequence + 1
            repetition = 0
        }else if(level%3 == 2){ 
            nCard = nCard + 1
            repetition = 0 
        }else{
            repetition = 1
        }
    }else{
        if(level%2 != 0){
            nCard = nCard + 1
            repetition = 0 
        }else{
            repetition = 1
        }
    }
}

function startGame() {
    var time = getTime()
    if(level >= maxLevel){
        endFunction()
    }
    else{
        container[0].appendChild(deck1);

        let shuffledDeck = shuffle(symbols);
        sequenceCard = [];
        matchCard = [];
    
        setGame()
        if(level==1){
            start = new Date();
            file["partita"]["orario_inizio"] = time
        }
        timing()
        levelStartTime = new Date();
        file["partita"]["livello"][level] = {}
        file["partita"]["livello"][level]["n_sequenza"] = nSequence
        file["partita"]["livello"][level]["n_carte"] = nCard
        file["partita"]["livello"][level]["ripetizione"] = repetition
        file["partita"]["livello"][level]["n_errori"] = 0
        file["partita"]["livello"][level]["n_aiuti"] = 0
        file["partita"]["livello"][level]["orario_inizio"] = time
        file["partita"]["livello"][level]["suggerimenti_abilitati"] = null

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
    buttonsRow.appendChild(endButton)
    file["partita"]["livello"][level]["sequenza"] = {}
    file["partita"]["livello"][level]["sequenza"][indexMatchCard] = {} 
    file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"] = {}
    file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}
}

function abilita_bottoni(){
    let time = getTime()
    if(file["partita"]["livello"][level]["suggerimenti_abilitati"]==null){
        file["partita"]["livello"][level]["suggerimenti_abilitati"] = time
    }
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
    myText.innerHTML = language_json.game.description[0] + level + ' \u00A0 \u00A0 \u00A0 ' + language_json.game.description[1] + score + ' \u00A0 \u00A0 \u00A0 ' + language_json.game.description[2] + minutes + ":" + seconds ;
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
    var time = getTime()
    var endTime = new Date()
    if(this.className == `card open show` && indexMatchCard!=nSequence){
        getSelectedCard(this);
        getRealCard()
    
        if(realCard === selectedCard){
            popupFunction('+ 10', '#27f198')
            lockMatch(deck1.childNodes[indexMatchCard])
            matchCard.push(realCard)
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "Corrispondenza"
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time
            mossa = 0
            score += 10
            scoreLevel += 10
            indexMatchCard += 1;
    
            for (let i=0; i<hideCards.length; i++){
                displayCard(deck2.childNodes[hideCards[i]])
            }
            hideCards = []
            hideCardsItem = []

            if(indexMatchCard==nSequence){      
                clearTimeout(timeout)

                // Tempo da msec a sec (/1000)
                file["partita"]["livello"][level]["tempo_parziale"] = (endTime.getTime() - levelStartTime.getTime())/1000
                file["partita"]["livello"][level]["orario_fine"] = time 
                file["partita"]["livello"][level]["terminato"] = 1
                file["partita"]["livello"][level]["n_errori"] = nWrongLevel
                file["partita"]["livello"][level]["n_aiuti"] = nHelpLevel
                file["partita"]["livello"][level]["score_parziale"] = scoreLevel
                                  
                if(level==1){
                    players.push({'level':parseInt(level),'player': parseInt(player),'score':parseInt(score)})
                }else{
                    var index = players.findIndex(obj => obj.player==player);
                    players[index] = {'level':parseInt(level),'player': parseInt(player),'score':parseInt(score)}
                }
                players.sort((a,b)=> (b.score - a.score || a.player - b.player));
                var index = players.findIndex(obj => obj.player==player);

                setTimeout(function(){
                    let tr = document.createElement("tr")
                    let td = document.createElement("td")
                    td.innerHTML = ''
                    tr.appendChild(td)

                    td = document.createElement("td")
                    td.innerHTML = language_json.game.table[0]
                    tr.appendChild(td)

                    td = document.createElement("td")
                    td.innerHTML = language_json.game.table[1]
                    tr.appendChild(td)
                    table.appendChild(tr)
                    let itr = (players.length<10) ? players.length : 10
                    for(let i=0; i<itr;i++){
                        let tr = document.createElement("tr")
                        let td = document.createElement("td")
                        td.innerHTML = i+1
                        tr.appendChild(td)
                        
                        td = document.createElement("td")
                        if(index==i){
                            tr.classList.add("selected");
                            td.innerHTML = language_json.game.table[2] //"User " + players[i]['player']
                        }else{
                            td.innerHTML = "User " + players[i]['player'] //language_json.game.table[3]
                        }
                        tr.appendChild(td)

                        td = document.createElement("td")
                        td.innerHTML = players[i]['score']
                        tr.appendChild(td)
                        table.appendChild(tr)
                    }
                    
                    let tr2 = document.createElement("tr")
                    td = document.createElement("td")
                    td.innerHTML = "..."
                    tr2.appendChild(td)
                    td = document.createElement("td")
                    tr2.appendChild(td)
                    td = document.createElement("td")
                    tr2.appendChild(td)

                    if(index >= 10){
                        tr = document.createElement("tr")
                        tr.classList.add("selected");

                        td = document.createElement("td")
                        td.innerHTML = index+1
                        tr.appendChild(td)
                        
                        td = document.createElement("td")
                        td.innerHTML = language_json.game.table[2] //"User " + players[index]['player']
                        tr.appendChild(td)

                        td = document.createElement("td")
                        td.innerHTML = players[index]['score']
                        tr.appendChild(td)

                        if(index == 10){
                            table.appendChild(tr)
                            table.appendChild(tr2) 
                        }else{
                            table.appendChild(tr2)
                            table.appendChild(tr)                          
                        }
                    }else{
                        table.appendChild(tr2) 
                    }

                    if(level >= maxLevel){
                        document.getElementById("next").style.display = "none"
                    }

                    buttonModal.click()
                }, 1000);        
            }else{
                file["partita"]["livello"][level]["sequenza"][indexMatchCard] = {} 
                file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"] = {}
                file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}
            }
        } else {
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "Errore"
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time
            mossa += 1
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}

            popupFunction('- 5', '#cf2c2c')
            score -= 5
            scoreLevel -= 5
            nWrongTot += 1
            nWrongLevel += 1

            wrongCards.push(this)
            wrongSelection(this)

            setTimeout(function(){
                for (let i=0; i<wrongCards.length; i++){
                    displayCard(wrongCards[i])
                    wrongCards.pop(this)
                }
            }, 100);
        }
        myText.innerHTML = language_json.game.description[0] + level + ' \u00A0 \u00A0 \u00A0 ' + language_json.game.description[1] + score + ' \u00A0 \u00A0 \u00A0 ' + language_json.game.description[2] + minutes + ":" + seconds ;
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

function randomIntFromInterval(min, max) { // min and max included 
    return Math.floor(Math.random() * (max - min + 1) + min)
  }

betaButton2.addEventListener("click", function() {
    disabilita_bottoni()
    var time = getTime()
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
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "SuggerisciPosizione(suggerimento)" 
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["nCarte_nonNascoste"] = selection.length + 1
            mossa += 1
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}
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
            selection = selection.filter(x => hideCardsItem.indexOf(x) === -1)
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa-1]["nCarte_nonNascoste_dopo"] = selection.length + 1

            popupFunction('- 2', '#0c96ff')
            score -= 2
            scoreLevel -= 2
            nHelpTot += 1
            nHelpLevel += 1
        }
    }  
    abilita_bottoni()
});

betaButton1.addEventListener("click", function() {
    disabilita_bottoni()
    var time = getTime()
    if(indexMatchCard!=nSequence){
        getRealCard() 
        var selection = cards.filter(x => x != realCard);
        selection = selection.filter(x => hideCardsItem.indexOf(x) === -1);

        if(selection.length != 0){
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "NascondiCarta(suggerimento)"
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["nCarte_nonNascoste"] = selection.length + 1
            mossa += 1
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}

            popupFunction('- 1', '#0c96ff')
            score -= 1
            scoreLevel -= 1
            nHelpTot += 1
            nHelpLevel += 1

            var item = selection[Math.floor(Math.random()*selection.length)];
            const index = cards.findIndex(object => {
                return object === item;
            });

            hideCard(deck2.childNodes[index])
            hideCards.push(index)
            hideCardsItem.push(item)

            selection = selection.filter(x => hideCardsItem.indexOf(x) === -1)
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa-1]["nCarte_nonNascoste_dopo"] = selection.length + 1
        }
    }
    abilita_bottoni()
});

betaButton3.addEventListener("click", function() {
    disabilita_bottoni()
    var time = getTime()
    if(indexMatchCard!=nSequence){
        getRealCard() 
        var selection = cards.filter(x => x != realCard);
        selection = selection.filter(x => hideCardsItem.indexOf(x) === -1);

        if(selection.length != 0){
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "IndicaPosizione(suggerimento)" 
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["nCarte_nonNascoste"] = selection.length + 1
            mossa += 1
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}

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
            scoreLevel -= 3
            nHelpTot += 1
            nHelpLevel += 1

            selection = selection.filter(x => hideCardsItem.indexOf(x) === -1)
            file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa-1]["nCarte_nonNascoste_dopo"] = selection.length + 1
        }
    }
    abilita_bottoni()
});

betaButton4.addEventListener("click", function() {
    var time = getTime()
    if(indexMatchCard!=nSequence){
        disabilita_bottoni()

        file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "RivediSequenza(suggerimento)"
        file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time 
        mossa += 1
        file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}

        popupFunction('- 4', '#0c96ff')
        score -= 4
        scoreLevel -= 4
        nHelpTot += 1
        nHelpLevel += 1

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

endButton.addEventListener("click", function() {
    file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "TerminaDurantePartita "
    file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = getTime() 
    mossa += 1
    file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa] = {}

    clearTimeout(timeout)
    buttonModal3.click()
});


function endFunction() {
    end = new Date();
    var time = getTime()
    file["partita"]["orario_fine"] = time

    if(indexMatchCard<nSequence){      
        // Tempo da msec a sec (/1000)
        file["partita"]["livello"][level]["tempo_parziale"] = (end.getTime() - levelStartTime.getTime())/1000 
        file["partita"]["livello"][level]["orario_fine"] = time 
        file["partita"]["livello"][level]["terminato"] = 0
        file["partita"]["livello"][level]["n_errori"] = nWrongLevel
        file["partita"]["livello"][level]["n_aiuti"] = nHelpLevel
        file["partita"]["livello"][level]["score_parziale"] = scoreLevel

        file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["tipo"] = "Si(Fine)"
        file["partita"]["livello"][level]["sequenza"][indexMatchCard]["mossa"][mossa]["orario"] = time        
    }
    
    file["partita"]["livello_raggiunto"] = level
    file["partita"]["score_tot"] = score
    file["partita"]["errori_tot"] = nWrongTot
    file["partita"]["aiuti_tot"] = nHelpTot
    // Tempo da msec a sec (/1000)
    file["partita"]["tempo_tot"] = (end.getTime() - start.getTime())/1000 

    $.ajax({
        url:"/test",
        type:"POST",
        contentType: "application/json",
        data: JSON.stringify(JSON.stringify(file)),
        success: function(result) {
            console.log("Result:");
            console.log(result);
            location.href = "end";
        }
    });
}

function addZero(i) {
    if (i < 10) {i = "0" + i}
    return i;
}

function getTime(){
    const d = new Date();
    let h = addZero(d.getHours());
    let m = addZero(d.getMinutes());
    let s = addZero(d.getSeconds());
    let mm = addZero(d.getMilliseconds());
    let time = h + ":" + m + ":" + s + ":" + mm;
    return time
}

function getDate(){
    const d = new Date();
    let day = addZero(d.getDate());
    let month = addZero(d.getMonth() + 1);
    let year = d.getFullYear();
    let h = addZero(d.getHours());
    let m = addZero(d.getMinutes());
    let s = addZero(d.getSeconds());
    let mm = addZero(d.getMilliseconds());
    let date = day + "-" + month + "-" + year + "_" + h + "_" + m + "_" + s + "_" + mm;
    return date
}
