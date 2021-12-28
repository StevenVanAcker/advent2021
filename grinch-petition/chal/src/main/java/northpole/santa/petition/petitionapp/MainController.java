package northpole.santa.petition.petitionapp;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@RestController
public class MainController {

    private static final Logger logger = LogManager.getLogger("Petitions");

    @RequestMapping(value = "/signPetition", method = RequestMethod.POST)
    public String sendMessage(@RequestParam(value = "name") String name,
            @RequestParam(value = "message") String message, @RequestParam(value = "recipient") String recipient) {
        if (recipient.equals("Grinch")) {
            return "Thank you for signing the petition!";
        }

        logger.info("Received unauthorized message for " + recipient);
        return "Tampering detected, this incident will be reported, you evil hacker!";
    }
}
