var reset = document.getElementById("reset");
reset.onclick = function() {
	if(confirm("Are you sure you want to erase all progress?")) {
		localStorage.removeItem("name");
		localStorage.removeItem("gameid");
		window.location = "/";
	}
}
