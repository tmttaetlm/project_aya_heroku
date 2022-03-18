'use strict'

window.onload = function() {
    
    //Catches clicks and send to handler
    document.addEventListener("click", function (event) {
        clickHandler(event.target);
    });

}

function clickHandler(obj) {
    if (obj.classList[0] == 'user-tg') {
        obj.children[0].click();
    }
}