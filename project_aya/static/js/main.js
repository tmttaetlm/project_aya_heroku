'use strict'

var timerId = 0,
    relX = 0,
    relY = 0;

window.onload = function() {

    //Catches clicks and send to handler
    document.addEventListener("click", function (event) {
        clickHandler(event.target);
    });

    //Catches mousemove and send to handler
    document.addEventListener("mouseover", function (event) {
        mouseoverHandler(event.target, event.pageX, event.pageY);
    });
    document.addEventListener("mouseout", function (event) {
        mouseoutHandler(event.target);
    });
    document.addEventListener("mousemove", function (event) {
        mousemoveHandler(event.target, event.pageX, event.pageY);
    });
}

function clickHandler(obj) {
    if (obj.classList[0] == 'user-tg') {
        obj.children[0].click();
    }
}

function mouseoverHandler(obj, pageX, pageY) {
  if (obj.classList[0] == 'leftBlock') {
    clearInterval(timerId)
    timerId = setInterval(() => {
      obj.parentElement.scrollLeft = obj.parentElement.scrollLeft - (80 -relX)/2.5;
      if (obj.parentElement.scrollLeft <= obj.parentElement.scrollLeftMax) {
        document.getElementsByClassName('rightBlock')[0].classList.remove('hide');
        document.getElementsByClassName('rightBlock')[0].classList.add('show');
      } else {
        document.getElementsByClassName('rightBlock')[0].classList.add('hide');
        document.getElementsByClassName('rightBlock')[0].classList.remove('show');
      };
    }, 5)
  }
  if (obj.classList[0] == 'rightBlock') {
    clearInterval(timerId)
    timerId = setInterval(() => {
      obj.parentElement.scrollLeft = obj.parentElement.scrollLeft + relX/2.5;
      if (obj.parentElement.scrollLeft >= 0) {
        document.getElementsByClassName('leftBlock')[0].classList.remove('hide');
        document.getElementsByClassName('leftBlock')[0].classList.add('show');
      } else {
        document.getElementsByClassName('leftBlock')[0].classList.add('hide');
        document.getElementsByClassName('leftBlock')[0].classList.remove('show');
      };
    }, 5)
  }
}
function mouseoutHandler(obj) {
  clearInterval(timerId);
  if (obj.classList[0] == 'leftBlock') {
    if (obj.parentElement.scrollLeft == 0) {
      obj.classList.add('hide');
      obj.classList.remove('show');
    } else {
      obj.classList.remove('hide');
      obj.classList.add('show');
    };
  }
  if (obj.classList[0] == 'rightBlock') {
    if (obj.parentElement.scrollLeft == obj.parentElement.scrollLeftMax) {
      obj.classList.add('hide');
      obj.classList.remove('show');
    } else {
      obj.classList.remove('hide');
      obj.classList.add('show');
    };
  }
}
function mousemoveHandler(obj, pageX, pageY) {
  if (obj.classList[0] == 'leftBlock' || obj.classList[0] == 'rightBlock') {
    let objRect = obj.getBoundingClientRect();
    relX = pageX - objRect.left;
  }
}
