//this can be used pretty much anywhere you just need to add the functions and event listner in the correct place.

this.chatEvent = function (nick, msg) {
    if (nick) {
        var lowerMsg = msg.toLowerCase();
        if (lowerMsg.startsWith("?chat ")) {
            var chatQuestion = msg.split(" ").slice(1).join(" ");
            this.chat(chatQuestion);
        }
        if (lowerMsg.endsWith("?")) {
            this.chat(msg);

        }
    }
};

this.chat = function (question) {
    var chatQuestion = question.split(" ").slice(1).join(" ");
    say("!Thinking...");
    FileAction.write("chatbot/question.txt", chatQuestion);
    delay(3000);
    let answerString = FileAction.read("chatbot/answer.txt");
    let maxChars = 250;
    if (answerString) {
        let chunks = [];
        while (answerString.length > maxChars) {
            let pos = answerString.lastIndexOf(' ', maxChars);
            let chunk = answerString.slice(0, pos);
            chunks.push(chunk);
            answerString = answerString.slice(pos + 1); // +1 to remove the space
        }
        chunks.push(answerString);

        chunks.forEach((chunk) => {
            say("!" + chunk);
            delay(5000); // 5 second delay between each message
        });
        FileTools.remove("chatbot/answer.txt");
    };



    addEventListener("chatmsg", this.chatEvent);