if ("name" in localStorage) {
	var name = localStorage.getItem("name");
	var el = document.getElementById("goldstar");
	var elname = document.getElementById("name");
	elname.innerText = name;
	el.classList.add("active");
}

var restart = document.getElementById("restart");
restart.onclick = function () {
	window.location = "/";
}

santael = document.createElement("div");
santael.hidden = true;
santael.id = "santa";
santael.innerHTML = "<p>Thanks for saving Christmas!!</p>";
document.body.appendChild(santael);

var bla = document.body;
bla.onclick = function () {
	var audio = new Audio('santabells.mp3');
	audio.play();
	santael.hidden = false;

	setTimeout(function () {
		santael.hidden = true;
	}, 3000);
}