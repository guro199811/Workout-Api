This API powers a workout application designed to empower users to achieve their fitness goals. 
It offers a secure authentication system, personalized goal tracking, customizable workout creation, 
weight tracking, and a library of preset exercises.

**Current Features:**

* User Creation


**Installation Steps:**
* Provided requirements.txt has every dependency needed
* Requires Docker and docker compose
* Navigate to project folder and run ```docker compose up --build```
Run uvicorn: 'uvicorn main:app'


**API Endpoints (Examples):**
* Register New User: ```POST /auth/```
* Requires Authentificated ```User: /user```

