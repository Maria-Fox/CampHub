CampHub, the first website to host a live environemnt for technical Bootcamp students to connect. 

[Visit CampHub] (https://visit-camphub.herokuapp.com/camphub)


Introduction/ Functionality

Designed to assist prospectice and current bootcamp students in navigating the bootcamp questions, confusion, frustrations, and networking world. Simply put- to provide overall support for this growing community. Users may interact in one of the following ways:

1 - Review and comment on the WordPress (API) CampHub Blog Articles through this application. Due to the API limitations users were unable to create their own posts. This severely limits the discussion for the community. To remedy this problem, this application includes added functionality so users can create their own topics of dispucssions (user posts). 

2 - Create user posts to discuss desired topic with community.

3 - Comment on user posts. 

4 - Should a user want to discuss a topic, but perhaps unsure/ uncomfortable of posting the discussion topic under their account they may "Suggest a Topic." This is logged in the db and the CampHub WordPress moderator can then review and post under the main account for user discussion. 

To read more about the "why" of CampHub please visit [CampHub] (https://visit-camphub.herokuapp.com/camphub/breakdown). As this was a passion project, I am confident additional features will be added. 


Standard User Flow:

Upon visiting [CampHub] (https://visit-camphub.herokuapp.com/camphub) a user is greeted with a few options -  
    1 - Learning about CampHub 
    2 - Creating an Account 
    3 - Logging In

    Walking through an exisitng user account User begins by clicking on "log in" after submitting valid credentials the User is then redirected to the CampHub User page. Here, the User is then presented with more options including:

    1 - Viewing Wordpress Articles
    2 - Viewing CampHub User Posts
    3 - Creating a Post
    4 - Suggesting a Topic
    5 - Updating Profile
    6 - Requesting Directions for Site


    Walking through the "Viewing Wordpress Articles" option. User begins by clicking option, upon click all WordPress articles are rendered including topic, data posted, author, and article content. Here, user can review all articles and then choose from additional additions including making an in-app comment or, interacting with WordPress and making a comment there.

    Similar features and routes appear for in-app user posts and comments. Based on user navigation, and user credentials options will vary. Authors of a given post or comment may edit or delete accordingly.


API

CampHub is interacting with [WordPress] (https://developer.wordpress.com/docs/api/), a REST API. I am also the CampHub WordPress creator/moderator which better allows me to quickly approve and render WordPress comments. 


Tech Stack

Backend/ Validations: CampHub uses Python for the back end with Flask (framework). FlaskWTForms is utilized for form validation.

Database: Flask_SQLAlchemy used in conjunction with PostresSQL. 

Styling/ HTML: The templates are rendered with jinja. CSS styling for the majority, with small BootStrap implementations.

Testing: Unit and integration testing completing using Flask Unittest.



Goals to Expand CampHub:

  - Design - update to better implement BootStrap. While the CSS implimentation was a great     refresher, I've noticed Heroku will make slight changes to the CSS design/ layout. 
  - Create a "Rate Bootcamp" feature which a measuring metrics. Metrics to be determined. 
  - Create a "Review Bootcamp" feature which a measuring metrics. Metrics to be determined. 
  - Allow Users to request adding a Bootcamp for ratings/ reviews.
  - Refactor form pages to cut down on repitition.
  - Include user bio and image for more personalization. 
  - Include secondary API (likely YouTube) to incorporate videos for users to navigate and see videos re: "a day in the life of.. ". Aimed for prospective students to further explore career.