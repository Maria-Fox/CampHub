CampHub

Link to API: Wordpress: https://developer.wordpress.org/rest-api/

1. What goal will your website be designed to achieve?

- Create a blog style website designed for bootcamp students to chat about boot camp experiences, post advice re: networking, ask industry questions, etc. This would be different from LinkedIn in that it’s not an environment to sell your experience/ get a job. It’s more of an open space to chat about frustrations, challenges, and lived experiences to uplift and provide guidance to bootcamp students.

2. What kind of users will visit your website? In other words, what is the demographic of your users?

The demogrpahic includes bootcamp students- this can be data science, software dev, cyber security- students generally in any technical environment/ field of study.

3. I will be collecting the following data:

Users: name, username, password, school name, field of study
posts: title, description, user_who_posted, likes(count), comments
Perhaps create communities? For ex -> all devs, -> all cyber sec. etc.

4. In brief, outline your approach to creating your project (knowing that you may notknow everything in advance and that these details might change later). Answer
   questions like the ones below, but feel free to add more information:

a. What does your database schema look like?

_subject to change as project progresses_ Please see .png file or models.py file.

Likely going to come back and add "groups" - endpoint that would allow students to break into their respective field chats rather than an all open discussion. I'll await for user feedback to make changes.

b. Issues that may arrise while working with the Blogger API include the API itself being down, or OAUTH2 Google server not working.

c. The only sensitive information to hide is the user password which will be encoded by bcrypt.

d. Functionality includes: Ueser creating account, chatting w/ other users. Liking/ commenting on user bloggs. Etc.

e. The first 3 user flows includes:
1- user visits website & clicks "create" adding a username, password, and profile image url. Formally welcomed to app.

2 User flow 1 + user hits "create blog/ post" user adds title and description is post fields. User hits "post" button and blog is rendered on the page.

3- User flow 1 + 2, + user can review and interact with other blog posts on-site.

f. I plan on implimenting a few button/ links to articles and study/ anxiety approach techniques within the application. Include community guideines ad student support fetaures to really tailor it to a student. For stretch goals, I can see creating a LinkedIn group for users who re ready to target job searching so the community grows together.
