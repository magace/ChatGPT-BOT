# ChatGPT BOT

A simple way to send and receive requests from chat gpt.

What does this do?  Basically you use kolbot or stealthbot to create a question.txt file with whatever question you have.  The python script monitors whatever folders you put in the config file.  If it finds a question.txt file it reads it sends the question to chat GPT api and creates a answer.txt in the same directory with the answer.  Kolbot or stealthbot then reads the answer file and says the results.  Pretty simple.

TODO:  Report username that ask questions back to discord.  Clean up discord hook. Fix estimated cost.  It's calculating too high.  Find a asian to test the unicode for chinese lettering.  Add error handling with stealthbot sometimes it hangs up if something goes wrong.  Make the kolbot use a worker until the answer file is there.  

Here are some pictures of it in use...

In game:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/bc4fa544-b0fe-4488-8c1a-4de36bd91122)

Stealthbot:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/3b871513-092b-48ac-a0de-d069e0a0e72d)

Discord (needs work):  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/22685d3e-0003-466b-9f59-2a80c80e1b66)

Console:  
![image](https://github.com/magace/ChatGPT-BOT/assets/7795098/d1cf2660-e6ea-4f0c-a8e3-86c62cb6ced3)
