import './src/styles.scss';
import { terminal } from './src/terminal.js';

const { Command, CommandResult } = require("./grinchbase_pb")
const { GrinchBaseClient } = require("./grinchbase_grpc_web_pb")

// Banner text
const banner = `
You have found the Grinch Base
-- Type 'help' to start --
`;

function makeid() {
	var result = '';
	var characters = '0123456789abcdef';
	for (var i = 0; i < 32; i++) {
		result += characters.charAt(Math.floor(Math.random() * 16));
	}
	return result;
}

var alldone = false;

function texthandler(client, term, txt, outputfn) {
	if (alldone) {
		document.body.classList.add("fadeout");
		setTimeout(function () {
			window.location = "/thanks.html";
		}, 3300)
		return;
	}

	var cmd = new Command();
	cmd.setText(txt);

	client.handleCommand(cmd, { "x-game-auth": localStorage.getItem('gameid') }, (err, response) => {
		var outputmsg = "";
		if (response.getCode() != 0) {
			outputmsg = "[ERROR] ";
		}
		outputmsg += response.getText();
		console.log(response.getType() + " " + outputmsg);
		outputfn(outputmsg);

		if (response.getType() == "name") {
			localStorage.setItem('name', response.getExtra());
			alldone = true;
		}
	});
}

const load = () => {
	var url = window.location.protocol + "//" + window.location.hostname;
	var client = new GrinchBaseClient(url);

	var gameid = localStorage.getItem('gameid');

	if (gameid == null) {
		console.log("Game ID not found, generating one.");
		gameid = makeid();
		localStorage.setItem("gameid", gameid);
	}

	console.log("started with Game ID " + gameid);

	const term = terminal({
		prompt: () => `$ / > `,
		banner,
		handlefn: (txt, outputfn) => texthandler(client, term, txt, outputfn),
	});
};

document.addEventListener('DOMContentLoaded', load);


