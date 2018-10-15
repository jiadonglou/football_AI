Football AI
------------------
Functionality:
	1. chat with user
	2. search for games (according to Date, Time, playing teams and match Number)
	3. follow games (Recieve live notification about game score)
	4. follow bets (Recieve live notification about betting rates)
	5. ask for prediction (win tie lose probability)
-----------------
Project Requirement:
	1. RASA_NLU (Process message)
	2. Sports API (Get match info)
	3. Bet365 API (Get Betting info)
	4. WeChat (Front-end)
	5. SQL (Store User preference)

-----------------
Code Syntax:

State : 
	1. INIT (0 / 1)
	2. FIND_MATCH (1 / "find_match")
	3. FOLLOW_MATCH (2 / "follow_match")
	4. GET_PREDICTION (3 / "get_prediction")
	5. GET_BETTING (4 / "get_betting")

User Input ("Find Match")-> State 

Install:
brew install ffmpeg --with-libvorbis --with-sdl2 --with-theora