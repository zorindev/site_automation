
chrome.tabs.onUpdated.addListener( function (tabId, changeInfo, tab) {

	
	function encodeToPassToContentScript(obj){
	    //Encodes into JSON and quotes \ characters so they will not break
	    //  when re-interpreted as a string literal. Failing to do so could
	    //  result in the injection of arbitrary code and/or JSON.parse() failing.
	    return JSON.stringify(obj).replace(/\\/g,'\\\\').replace(/'/g,"\\'")
	}
	
	if(tab.url.indexOf('tickets.rugbyworldcup.com') != -1 && changeInfo.status == 'complete') {
		
		var storage = window.localStorage;
		var credentials = storage.getItem("credentials");

		chrome.tabs.executeScript({
		    code: "var credentials = JSON.parse('" + encodeToPassToContentScript(credentials) + "');"
		}, function () {
		    chrome.tabs.executeScript({
		        file: "inject.js"
		    });
		});
		    
    }
    
});


// TODO: establish communication with the back end to close the tab
// https://developer.chrome.com/extensions/messaging

chrome.runtime.onMessage.addListener(
	  function(request, sender, sendResponse) {
		  if (request.type == "closeTab") {
			  chrome.tabs.remove(sender.tab.id);
		  }
		  
		  chrome.tabs.executeScript(sender.tab.ib, {
				code: "console.log(' ok 1');"
			});  
		  
	  });


