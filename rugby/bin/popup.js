
document.addEventListener('DOMContentLoaded', function() {

	var storage = window.localStorage;
	
	var start_button = document.getElementById("statrBotBtn");
	var stop_button = document.getElementById("stopBotBtn");
	
	
	start_button.addEventListener('click', function() {
		var credentials = document.getElementById("credentials").value;
		storage.setItem("credentials", credentials);
		chrome.tabs.create({url: 'https://hidden.url'}, function(tab){});
	});
	
	stop_button.addEventListener('click', function() {	
		chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
			chrome.tabs.remove(tabs[0].id);
		});
		
	});
	
});