// this is the code which will be injected into a given page...

var max_attempt = 10;
var current_attempt = 0;

var snd = new Audio("data:audio/mp3;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");
var beep_interval_id = null;
var beep_count = 0;
var max_beep = 5;


var storage = window.localStorage;
var storage_key_sfx = "rugby_bot";


var identities = {
	"username": "Match 45",
};

var creds = credentials.split(":");
var identity = "";
if(creds.length > 0) {
	identity = creds[0];
}

(function() {

	function doLogin() {
		
		if(credentials) {
			
			if(credentials.includes(":")) {
				var creds = credentials.split(":");
				
				try {
					document.getElementById("login").value = creds[0];
					document.getElementById("login").text = creds[0];
					document.getElementById("password").value = creds[1];
					document.getElementById("password").text = creds[1];
					
					try {
						var evObj = document.createEvent('Events');
						evObj.initEvent("onmouseover", true, false);
						document.getElementsByClassName("rc-anchor-center-container")[0].dispatchEvent(evObj);
						document.getElementsByClassName("recaptcha-checkbox-checkmark")[0].click()
						document.querySelector("input[name='doLogin']").click()
					}
					catch(err) {
						console.log(" error occured ");
						console.log(err);
						
						alert(" Perform the captcha verification manually and click login ")
					}
				} catch(err) {
					console.log(err);
				}
			} 
		}
		
	}
	
	function handleAgreementPage() {
		storage.clear();
		document.querySelector("input[name='doUpdateSegmentInfo']").click();
	}
	
	function handleProductListPageOff() {
		
		storage.clear();
		storage.setItem("311_CAT A", "311_CAT A");
		
		var url = "https://hidden.url";
		//window.open(url, "", 'height=640,width=960,toolbar=no,menubar=no,scrollbars=no,location=no,status=no');
		var iframe = document.createElement('iframe');
		iframe.setAttribute("src", url);
		//a.setAttribute("target", "_blank")
		//a.setAttribute("id", "311_CAT A");
		//document.body.appendChild(a);
		//a.click();
		
	}
	
	function handleProductListPage() {
		
		// runs every 20 seconds 
		//setInterval(function(){
		//storage.clear();
			local_storage_keys = Object.keys(storage);
			
			console.log(local_storage_keys);
			var count_of_keys = 0;
			for(var key in local_storage_keys) {
				item = local_storage_keys[key];
				if(item != null) {
					console.log(key);
					console.log(item)
					console.log(item.includes(storage_key_sfx));
					if(item.includes(storage_key_sfx)) {
						count_of_keys += 1;
					}
				}
			}
			
			if(count_of_keys > 0) {
				console.log(" waiting for other tabs to close ");
				
			} else {
				console.log(" all tabs have been closed ");
				
				//return;
			
				prod_cntr = document.querySelector("div[class='productsContainer']");
				if(prod_cntr != null) {
					
					prod_list = prod_cntr.querySelectorAll("div.productContainer");
					
					
					console.log(prod_list);
					
					for(var i = 0; i < prod_list.length; i++) {
						
						
						var match_name = prod_list[i].querySelector("div.matchContainer > div.info > span").innerText;
						
						console.log(i);
						console.log(match_name);
						console.log(identity);
						console.log(identities);
						
						if(identities[identity] == match_name) {
							
							console.log(" IT WAS A MATCH ");
						
							var prod_id = prod_list[i].getAttribute("data-idproduct");
							console.log(prod_id);
						
							price_list = prod_list[i].querySelectorAll("div.priceItem");
						
							for(var k = 0; k < price_list.length; k++) {
							
								// if DIV with error does not exist
								if(price_list[k].querySelector("div") == null) {
									// register a key in storage
									category = price_list[k].querySelectorAll("span")[0].innerText;
									category = category.replace("-", "").trim();
									category_key = storage_key_sfx + "_" + prod_id + "_" + category;
									storage.setItem(category_key, category_key);
									
									button = prod_list[i].querySelector("div.demand > div.buttons > input")
									button.setAttribute("target", "_blank")
									
									var a = document.createElement('a');
									a.setAttribute("href", "showProduct.html?idProduct=" + prod_id);
									a.setAttribute("target", "_blank")
									a.setAttribute("id", category_key);
									document.body.appendChild(a);
									
									a.click();
								}
							}
						}
						
						break;
					}
				}
			}
		
		//;}, 2000);
	}
	
	function handleProductPage() {
	
		
		console.log(" in handleProductPage ");
		buy_tickets_button = document.querySelector("input[name='doAddToBasket']");
		
		current_attempt += 1;
		
		//ticket_list = document.querySelectorAll("div[class='productContainerSection priceColumn'] > div.priceRow > div[class='priceRowColumn ticketSelector']");
		
		ticket_list = document.querySelectorAll("div[class='productContainerSection priceColumn'] > div.priceRow");
		
		tickets_available = false;
		
		console.log(" ticket_list.length ");
		console.log(ticket_list.length);
		
		for(var i = 1; i < ticket_list.length; i++) {
			
			var category_key = null;
			var category = ticket_list[i].querySelectorAll("span")[0].innerText.replace('-', '').trim().replace('"', '');
			var url = new URL(window.location.href);
			var prod_id = url.searchParams.get("idProduct");
			if(prod_id != null) {
				category_key = storage_key_sfx + "_" + prod_id + "_" + category;
			
				console.log(" we have category key");
				console.log(category_key);
				spans = ticket_list[i].querySelector("div[class='priceRowColumn ticketSelector']").querySelectorAll("span");
				
				if(spans.length == 2) {
				
					console.log(" we found spans ");
					// now we have the category key and we came across available ticket box
					// lets see if the key is in storage
					// if it is then remove the key and use this ticket box
					
					if(storage.getItem(category_key) != null) {
						
						console.log(" we found key");
						
						random_number_of_tickets = Math.floor(Math.random() * 2);
						if(random_number_of_tickets == 0) {
							random_number_of_tickets = 1;
						}
					
						console.log(" build tickets ");
						console.log(random_number_of_tickets);
						
						for(var tp = 0; tp < random_number_of_tickets; tp++) {
							spans[1].click()
						}
						
						tickets_available = true;
						storage.removeItem(category_key);
						// break the for loop to limit each page to one category
						break;

					} else {
						console.log(" storage.getItem(category_key) was null ");
						console.log(category_key);
					}

				} else {
					console.log(" did not find ctrl spans ");
					console.log(spans);
				}
			} else {
				console.log("parameter was not passed .. closing tab ");
				window.close();
			}
		}
		
		if(tickets_available) {
			
			console.log(" tikets available and clicking ");
			setTimeout(function(){buy_tickets_button.click();}, 2000);
		
		} else {
			window.close();
		}
	}
	
	
	function is_basket_page() {
		
		var rtn = false;
		var url = window.location.href.toLowerCase();
		if(url.includes("showbasket")) {
			rtn = true;
		}
		return rtn;
	}
	
	function beep() {
		
		if(beep_count < max_beep) {
			beep_count += 1;
			
			try{
				snd.currentTime = 0;
				snd.play();
			} catch(err) {
				
			}
			
		} else {
			clearInterval(beep_interval_id);
			window.history.back();
		}
	}
	
	
	function handleBasketPage() {
		beep_interval_id = setInterval(beep, 2000);
	}
	

	if(document.querySelector("input[name='doLogin']") != null) {
		doLogin();
		
	} else if(document.querySelector("input[name='doUpdateSegmentInfo']") != null) {
		handleAgreementPage();
		
	} else if(document.querySelector("div[class='productList']") != null) {
		handleProductListPage();
		
	} else if(document.querySelector("div[class='productContainer']") != null) {
		
		setTimeout( function(){ handleProductPage(); }, 2000);
		
	} else if(document.querySelector("input[id='doMakePayment']") != null || is_basket_page()) {
		handleBasketPage();
		
	} else {
		
		console.log("unidentified page");
		///window.close();
	}
	
	

})();