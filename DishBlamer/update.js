var oldData = null;

var update = function(){
	$.ajax({
	  dataType: "json",
	  url: "log.txt",
	  success: function(data){

	  	//no updates if data hasn't changed
	  	if (oldData!== null && data.length === oldData.length){
	  		return;
	  	}

	  	//if new data, show who added or removed a dish
	  	var thisRoundName = null;
	  	var thisRoundPositive = null;
	  	if (oldData !== null){
	  		for (var i = oldData.length; i<data.length; i++){
	  			//this represents a new item
	  			var name = data[i][0];
	  			thisRoundName = name;
	  			var color = "#EBFFD6";
	  			thisRoundPositive = true;
	  			if (parseInt(data[i][2]) === -1){
	  				color = "#FFD6DB";
	  				thisRoundPositive = false;
	  			}
	  			$("#notification").html("<div id='notification_inner' style='background-color:"+color+"'><div>"+name+"</div><img style='width:500px' src='"+data[i][3]+"'></div>");
	  			$("#notification").fadeTo(500, 1.0);
	  		}
	  	}

	  	//update the left leaderboard (returns vs checkouts)
	  	var scores = {};
	  	for (var i = 0; i<data.length; i++){
	  		var cells = data[i];
	  		var name = cells[0];
	  		scoreSoFar = scores[name];
	  		if (!scoreSoFar){ scoreSoFar = 0;}
	  		scoreSoFar+=parseInt(cells[2]);
	  		scores[name] = scoreSoFar;
	  	}
			var sortable = [];
			for (var name in scores)
			      sortable.push([name, scores[name]]);
			sortable.sort(function(a, b) {return a[1] - b[1]}).reverse();

	  	var tableStr = "<table style='width:400px'>";
	  	tableStr += "<thead><tr><th>User</th><th>Returns Minus Checkouts</th></tr></thead><tbody>";
	  	for (var i = 0; i<sortable.length; i++){
	  		var name = sortable[i][0];
	  		var score = sortable[i][1];
	  		var extra = "";
	  		if (name === thisRoundName){
	  			extra = "class='"+thisRoundPositive+"'";
	  		}
	  		tableStr += "<tr "+extra+"><td>"+name+"</td><td>"+score+"</td></tr>";
	  	}
	  	tableStr += "</tbody></table>";
	  	$("#returns").html(tableStr);

	  	//update the right leaderboard (average time before return)
	  	var timeSums = {};
	  	var numCheckoutReturnPairs = {}
	  	for (var i = 0; i<data.length; i++){
	  		var cells = data[i];
	  		if (parseInt(cells[2]) === 1){
	  			continue;
	  		}
	  		//we have a checkout!
	  		var name = cells[0];
	  		timeSumSoFar = timeSums[name];
	  		if (!timeSumSoFar){ timeSumSoFar = 0;}
	  		numCheckoutsSoFar = numCheckoutReturnPairs[name];
	  		if (!numCheckoutsSoFar){ numCheckoutsSoFar = 0;}

	  		for (var j = i; j<data.length; j++){
	  			var newCells = data[j];
	  			if (newCells[0] === name){
	  				if (newCells[2] === 1){
	  					var timeDiff = parseFloat(newCells[1])-parseFloat(cells[1]);
	  					timeSumSoFar += timeDiff;
	  					timeSums[name] = timeSumSoFar;
	  					numCheckoutReturnPairs[name] = numCheckoutsSoFar+1;
	  					break;
	  				}
	  			}
	  		}
	  	}
			sortable = [];
			for (var name in timeSums)
			      sortable.push([name, timeSums[name]/numCheckoutReturnPairs[name]]);
			sortable.sort(function(a, b) {return a[1] - b[1]});

	  	var tableStr = "<table style='width:400px'>";
	  	tableStr += "<tr><th>User</th><th>Average Return Time</th></tr>";
	  	for (var i = 0; i<sortable.length; i++){
	  		var name = sortable[i][0];
	  		var score = sortable[i][1];
	  		extra = "";
	  		if (name === thisRoundName){
	  			extra = "class='"+thisRoundPositive+"'";
	  		}
	  		tableStr += "<tr "+extra+"><td>"+name+"</td><td>"+score+"</td></tr>";
	  	}
	  	tableStr += "</tbody></table>";
	  	$("#times").html(tableStr);

	  	oldData = data;

	  	setTimeout(removeHighlights,1000);
	  }
	});

	setTimeout(update,500);
};
$(update);

var removeHighlights = function(){
	//fade the notification of user interaction with DishShamer
	$("#notification").fadeTo(2000, 0.0);
	setTimeout(function(){
		//remove the highlights on leaderboard rows affected by the user interaction
		$("tr").removeClass("false");
		$("tr").removeClass("true");
	},1700);
};