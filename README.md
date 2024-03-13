This API powers a workout application designed to empower users to achieve their fitness goals.
It offers a secure authentication system, personalized goal tracking, customizable schedule creation,
weight tracking, and a library of preset exercises.

API Is Created With Python FastAPI
Database: PostgreSQL
Database Management Application: PGadmin4 Accessable at Port `5050`

**Installation Steps:**

- Requires Docker and docker compose
- Provided requirements.txt has every Python dependency needed
- Navigate to project folder and run: `docker compose up --build`

**FastAPI Documentation Routes**

- Docs `/docs`
- Redocs `/redocs`

**API Endpoints (Examples):**

- Create User (POST):`/auth/register`
- Login/Token access (POST): `/auth/token`

- Retrieve Authenticated User Data (GET): `/user/`
- Change Authentificated User Data (PUT): `/user/data_change`

- Retrieve All Exercises (GET): `/exercise/`
- Retrieve Exercise by exercise_id (GET): `/exercise/{exercise_id}`
- Retrieve All Exercise types (GET): `/exercise/all_exercise_types`
- Retrieve all Exercise units (GET): `/exercise/all_exercise_units`

- Retrieve All Goal types (GET): `/goal/all_goal_types/`
- Create A User Specific Goal (POST): `/goal/create_goal/`
- Retrieve Authenticated User Goals (GET): `/goal/personal_goals/`
- Change Authenticated User Goal (PUT): `/goal/personal_goals/{goal_id}`
- Delete Authenticated User Goal (DELETE): `/goal/personal_goals/{goal_id}`

- Create A User Specific Schedule (POST): `/schedule/create_schedule/`
- Retrieve Authenticated User Schedules (GET): `/schedule/user_schedules/`
- Change Authenticated User Schedule (PUT): `/schedule/user_schedules/{goal_id}`
- Delete Authenticated User Schedule (DELETE): `/schedule/user_schedules/{goal_id}`

- Retrieve User Specific History (GET): `/history/`
- BMI History Addition, gets current user and adds bmi to history,
  needs specifying bmi value (POST): `/history/add_bmi_history/{bmi_value}`
- Delete Authenticated User History By ID (DELETE): `/history/{history_id}`
