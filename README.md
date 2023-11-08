# ChatGPT BOT

A simple way to send and receive requests from chat gpt.

What does this do?  Basically you use kolbot or stealthbot to create a question.txt file with whatever question you have.  The python script monitors whatever folders you put in the config file.  If it finds a question.txt file it reads it sends the question to chat GPT api and creates a answer.txt in the same directory with the answer.  Kolbot or stealthbot then reads the answer file and says the results.  Pretty simple.

TODO:  Report username that ask questions back to discord.  Clean up discord hook. Fix estimated cost.  It's calculating too high.  Find a asian to test the unicode for chinese lettering.  Add error handling with stealthbot sometimes it hangs up if something goes wrong.  Make the kolbot use a worker until the answer file is there.  

Here are some pictures of it in use...

In game:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/bc4fa544-b0fe-4488-8c1a-4de36bd91122)

Stealthbot:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/3b871513-092b-48ac-a0de-d069e0a0e72d)

Discord:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/0ddfa864-8496-4219-87ce-10db7d11d2f5)

Console:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/d1cf2660-e6ea-4f0c-a8e3-86c62cb6ced3)


Here is one possible way to add it to Kolbot.  Add something like this to your maptoolsthread or main kolbot toolsthread.
```
Save Questions:

Add chat event with all the other events:
  addEventListener("keyup", this.keyEvent);
  addEventListener("gameevent", this.gameEvent);
  addEventListener("scriptmsg", this.scriptEvent);
  addEventListener("chatmsg", this.chatEvent);

Create the chat even function:

  this.chatEvent = function (nick, msg) {
    if (nick) {
      var lowerMsg = msg.toLowerCase();
      if (lowerMsg.startsWith("?chat ")) {  //  This will save msg if someone types ?chat question
        var chatQuestion = msg.split(" ").slice(1).join(" ");
        say("!Thinking......");
        FileAction.write("chatbot/question.txt", nick + " " + chatQuestion);
      }
      if (lowerMsg.endsWith("?")) {  //  This will automatically respond to anything someone types ending with a question mark. "?"
        say("!Thinking......");
        FileAction.write("chatbot/question.txt", nick + " " + msg);
      }
    }
  }


Read Answers:

  this.checkAnswer = function () {
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
        delay(8000); // 5 second delay between each message
      });
      FileTools.remove("chatbot/answer.txt");
    }
  };

Next call it inside the main while loop:

  // Start
  while (true) {
    this.checkAnswer();
    try {```

