function onLoad() {
  window.setInterval(function(){
    getOutput("switcher-values")
            count++;
    }, 2000);
}

// javascript I nicked from something I wrote ages ago 
function getOutput(ThisObject) {
  ThisRequest="/".concat(ThisObject);
  getRequest(
    ThisRequest, // URL for the PHP file
    drawOutput,  // handle successful request
    drawError,    // handle error
    ThisObject // Place to put the message
  );
return false;
}
// handles drawing an error message
function drawError (thisStatus,thisObject) {
var container = document.getElementById(thisObject);
container.innerHTML = 'Uhoh... error: '.concat(thisStatus);
}
// handles the response, adds the html
function drawOutput(responseText, object) {
var container = document.getElementById(object);
container.innerHTML = responseText;
}
// helper function for cross-browser request object
function getRequest(url, success, error, object) {
var req = false;
try{
  // most browsers
  req = new XMLHttpRequest();
} catch (e){
  // IE
  try{
      req = new ActiveXObject("Msxml2.XMLHTTP");
  } catch (e) {
      // try an older version
      try{
          req = new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e){
          return false;
      }
  }
}
if (!req) return false;
if (typeof success != 'function') success = function () {};
if (typeof error!= 'function') error = function () {};
req.onreadystatechange = function(){
  if(req .readyState == 4){
      return req.status === 200 ?
          success(req.responseText, object) : error(req.status, object)
      ;
  }
}
req.open("GET", url, true);
req.send(null);
return req;
}

