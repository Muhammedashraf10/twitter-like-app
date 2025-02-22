# twitter-like-app

This repo contains a simple UI using react contains a signup, login and basic timeline pages for twitter-like app, the repo is built by the help of UI

# Frontend 
Directory Structure 


![image](https://github.com/user-attachments/assets/a256bf94-ce91-42ee-bf81-0ae22290024a)

# backend

- loginHandler.py: Validate if Users Exists or not, If users exists, the user redirected to the TweetPage
- signUpHandler.py: Validate if a user with the same name exists before signing up 
- PostTweets.py: Post a tweets and validate the number of charachters with  limits 280
- GetTweets.py: Get the tweets ( will be enhanced later on to get the tweets of the followers only)
- DeleteTweet.py: Delete the tweets only posted by the user and user is not authorized to delete tweets of other.
