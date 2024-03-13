from database import SessionLocal
from models import Exercise, Exercise_Type, Exercise_Unit, Goal_Type

import logging

db = SessionLocal()


# Exercise Type Data for easy filtering
exercise_type_data = [
    {"exercise_type_name": "Endurence"},
    {"exercise_type_name": "Strength"},
    {"exercise_type_name": "Balance"},
    {"exercise_type_name": "Flexibility"}
]


# Exercise unit types for unit management
exercise_unit_types = [
    {"unit_1": "Km", "unit_2": "M"},
    {"unit_1": "Sets", "unit_2": "Reps"}
]


# Goal Types for Filtering Goal Specific exercises
goal_types = [
    {"goal_target": "Weight"},
    {"goal_target": "Distance"},
    {"goal_target": "Speed"},
    {"goal_target": "Strength"}
]


# Premade With 20 Different Exercises
exercises_data = [
    {
        "exercise_name": "Push-ups",
        "description": "A bodyweight exercise that strengthens the chest, shoulders, triceps, and core.",
        "instructions": "Start in a high plank position with hands shoulder-width apart, core engaged, and back straight. Lower your chest towards the ground until your elbows bend at a 90-degree angle. Push back up to the starting position in a controlled manner.",
        "target_muscles": "Chest, Shoulders, Triceps, Core",
        "difficulty": "Intermediate",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Squats",
        "description": "A compound exercise that strengthens the legs, glutes, and core.",
        "instructions": "Stand with feet shoulder-width apart, toes slightly pointed outward. Lower your body as if sitting back in a chair, keeping your back straight and knees tracking over your toes. Descend until your thighs are parallel to the ground (or as low as your flexibility allows). Push back up to the starting position explosively.",
        "target_muscles": "Legs, Glutes, Core",
        "difficulty": "Beginner",
        "exercise_type_id": 3,
        "unit_type_id": 2,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Lunges",
        "description": "A unilateral exercise that strengthens the legs, core, and balance.",
        "instructions": "Stand with feet hip-width apart. Step forward with one leg, lowering your body until both knees are bent at 90-degree angles. Ensure your front knee doesn't track past your toes. Push back up to the starting position and repeat with the other leg.",
        "target_muscles": "Legs, Glutes, Core",
        "difficulty": "Intermediate",
        "exercise_type_id": 3,
        "unit_type_id": 2,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Deadlifts",
        "description": "A lower body exercise that strengthens the back, hamstrings, glutes, and core. (**Requires proper form to avoid injury**)",
        "instructions": "Stand with feet hip-width apart, holding a barbell or dumbbells in front of your thighs with a neutral grip (palms facing your body). Keeping your back straight and core engaged, hinge at the hips and lower the weight towards the ground, pushing your glutes back. Lower the weights until your arms are straight (or as far as your flexibility allows) without rounding your back. Stand back up to the starting position by squeezing your glutes and hamstrings.",
        "target_muscles": "Back, Hamstrings, Glutes, Core",
        "difficulty": "Advanced",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 2,
    },
    {
        "exercise_name": "Pull-ups",
        "description": "A bodyweight exercise that strengthens the back, biceps, and forearms. (**Requires a pull-up bar**)",
        "instructions": "Grasp a pull-up bar with an overhand grip (palms facing away from you) and hands shoulder-width apart. Hang with your arms fully extended. Pull yourself up until your chin clears the bar. Lower yourself back down in a controlled manner.",
        "target_muscles": "Back, Biceps, Forearms",
        "difficulty": "Advanced",
        "exercise_type_id": 4,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Rows",
        "description": "An exercise that strengthens the back and biceps.",
        "instructions": "You can perform rows using a barbell, dumbbells, or a rowing machine. The basic form involves hinging at the hips and keeping your back straight while pulling the weight towards your chest. There are variations for different equipment.",
        "target_muscles": "Back, Biceps",
        "difficulty": "Intermediate",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Overhead Press",
        "description": "An exercise that strengthens the shoulders, triceps, and core.",
        "instructions": "You can perform overhead press with a barbell or dumbbells. Start with the weight held at shoulder level, elbows bent at 90 degrees. Press the weight straight overhead in a controlled manner, keeping your core engaged. Slowly lower the weight back down to the starting position.",
        "target_muscles": "Shoulders, Triceps, Core",
        "difficulty": "Intermediate",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Bench Press",
        "description": "An exercise that strengthens the chest, triceps, and shoulders. (**Requires a bench press setup**)",
        "instructions": "Lie on a flat bench with the barbell held above your chest, arms fully extended. Lower the barbell down to your chest in a controlled manner, elbows tucked in at a 45-degree angle. Press the weight back up to the starting position explosively.",
        "target_muscles": "Chest, Triceps, Shoulders",
        "difficulty": "Advanced",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Plank",
        "description": "An isometric exercise that strengthens the core, shoulders, and back.",
        "instructions": "Start in a high push-up position with forearms flat on the ground, elbows shoulder-width apart, and body in a straight line from head to heels. Engage your core and glutes to maintain a stable position.",
        "target_muscles": "Core, Shoulders, Back",
        "difficulty": "Intermediate",
        "exercise_type_id": 3,
        "unit_type_id": 2,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Romanian Deadlift",
        "description": "A variation of the deadlift that targets the hamstrings and glutes.",
        "instructions": "Stand with feet hip-width apart, holding a barbell or dumbbells in front of your thighs with a neutral grip (palms facing your body). Keeping your back straight and core engaged, hinge at the hips and lower the weight towards the ground, pushing your glutes back. Lower the weight until your hamstrings feel tight (not rounding your back) and then return to the starting position by squeezing your glutes and hamstrings.",
        "target_muscles": "Hamstrings, Glutes",
        "difficulty": "Advanced",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Side Plank",
        "description": "An isometric exercise that strengthens the obliques and core.",
        "instructions": "Lie on your side with one elbow directly under your shoulder. Stack your feet on top of each other or stagger them for more stability. Engage your core and lift your hips off the ground, forming a straight line from head to heels. Hold for a desired time and then repeat on the other side.",
        "target_muscles": "Obliques, Core",
        "difficulty": "Intermediate",
        "exercise_type_id": 1,
        "unit_type_id": 2,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Bicep Curls",
        "description": "An isolation exercise that strengthens the biceps.",
        "instructions": "You can perform curls with dumbbells or a barbell. Hold the weight(s) at your sides with palms facing forward. Curl the weight(s) towards your shoulders, squeezing your biceps at the top. Slowly lower the weight(s) back down to the starting position.",
        "target_muscles": "Biceps",
        "difficulty": "Beginner",
        "exercise_type_id": 2,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Running",
        "description": "A cardiovascular exercise that strengthens the heart, lungs, and leg muscles.",
        "instructions": "Start with a warm-up walk or slow jog to prepare your body. Gradually increase your speed to a comfortable pace. Maintain a steady pace, keeping your body relaxed and moving in a smooth motion. Cool down with a slow jog or walk after your run.",
        "target_muscles": "Legs, Core",
        "difficulty": "Beginner to Advanced (depending on pace and distance)",
        "exercise_type_id": 1,
        "unit_type_id": 1,
        "goal_type_id": 2,
    },
    {
        "exercise_name": "Shoulder Raises",
        "description": "An exercise that strengthens the shoulders.",
        "instructions": "Hold dumbbells in each hand at your sides with palms facing your body. Raise your arms out to the sides until they are parallel to the ground, keeping your elbows slightly bent. Lower the weights back down to the starting position in a controlled manner.",
        "target_muscles": "Shoulders",
        "difficulty": "Beginner",
        "exercise_type_id": 4,
        "unit_type_id": 2,
        "goal_type_id": 4,
    },
    {
        "exercise_name": "Walking Lunges",
        "description": "A variation of lunges that adds a cardio element and works your core for stability.",
        "instructions": "Stand with feet hip-width apart. Step forward with one leg, lowering your body until both knees are bent at 90-degree angles. Ensure your front knee doesn't track past your toes. Push back up to the starting position and then step forward with the other leg. Continue alternating legs as you walk forward.",
        "target_muscles": "Legs, Glutes, Core",
        "difficulty": "Intermediate",
        "exercise_type_id": 3,
        "unit_type_id": 1,
        "goal_type_id": 3,
    },
    {
        "exercise_name": "Fast Walking",
        "description": "A low-impact cardiovascular exercise that strengthens the heart, lungs, and leg muscles.",
        "instructions": "Start with a warm-up walk at a slow pace. Gradually increase your speed to a brisk pace that raises your heart rate while still allowing for full breath control. Swing your arms naturally and keep your posture straight. Cool down with a slow walk after your fast walk.",
        "target_muscles": "Legs, Core",
        "difficulty": "Beginner",
        "exercise_type_id": 1,
        "unit_type_id": 1,
        "goal_type_id": 2,
    },
    {
        "exercise_name": "Calf Raises",
        "description": "An exercise that strengthens the calf muscles.",
        "instructions": "You can perform calf raises on the ground, a step, or a calf raise machine. Stand with your feet shoulder-width apart and raise up onto your toes. Hold for a second at the top and then slowly lower back down to the starting position.",
        "target_muscles": "Calves",
        "difficulty": "Beginner",
        "exercise_type_id": 3,
        "unit_type_id": 2,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Sprinting",
        "description": "A high-intensity cardiovascular exercise that strengthens the heart, lungs, and leg muscles.",
        "instructions": "Start with a warm-up jog to prepare your body. When ready, increase your speed to a full sprint for a short duration (20-30 seconds or 100-200 meters). After each sprint, allow for full recovery with a slow walk or jog. Repeat the sprint-recovery cycle for your desired number of repetitions.",
        "target_muscles": "Legs, Core",
        "difficulty": "Advanced",
        "exercise_type_id": 1,
        "unit_type_id": 1,
        "goal_type_id": 3,
    },
    {
        "exercise_name": "Bicycling",
        "description": "A low-impact cardiovascular exercise that strengthens the heart, lungs, and leg muscles.",
        "instructions": "Start with a slow pace to warm up. Gradually increase your speed and resistance as desired. Maintain a steady pace, keeping your body relaxed. Cool down with a slow pace and lower resistance.",
        "target_muscles": "Legs, Core",
        "difficulty": "Beginner to Advanced (depending on pace and resistance)",
        "exercise_type_id": 3,
        "unit_type_id": 1,
        "goal_type_id": 1,
    },
    {
        "exercise_name": "Jumping Jacks",
        "description": "A full-body cardiovascular exercise that strengthens the heart, lungs, and various muscle groups.",
        "instructions": "Stand with your feet together and your hands at your sides. Simultaneously raise your arms above your head and jump up just enough to spread your feet out wide. Without pausing, quickly reverse the movement and repeat.",
        "target_muscles": "Full Body",
        "difficulty": "Beginner",
        "exercise_type_id": 4,
        "unit_type_id": 2,
        "goal_type_id": 1,
    }
]


def populate_exercise(exercise_data, db=db):
    try:
        exercise_query = db.query(Exercise).first()
        if exercise_query is None:
            if exercise_data:
                for exercise in exercise_data:
                    new_exercise = Exercise(**exercise)
                    db.add(new_exercise)

            db.commit()
    except Exception as e:
        logging.error(e)
        db.rollback()


def populate_exercise_type(exercise_type_data, db=db):
    try:

        exercise_type_query = db.query(Exercise_Type).first()
        if exercise_type_query is None:
            if exercise_type_data:
                for exercise_type in exercise_type_data:
                    new_exercise_type = Exercise_Type(**exercise_type)
                    db.add(new_exercise_type)
            db.commit()
    except Exception as e:
        logging.warning(e)


def populate_exercise_unit(exercise_unit_type_data, db=db):
    try:
        exercise_unit_type = db.query(Exercise_Unit).first()
        if exercise_unit_type is None:
            if exercise_unit_type_data:
                for exercise_unit_data in exercise_unit_type_data:
                    new_exercise_unit_type = Exercise_Unit(
                        **exercise_unit_data)
                    db.add(new_exercise_unit_type)
            db.commit()
    except Exception as e:
        logging.warning(e)


def populate_goal_type(goal_types, db=db):
    try:
        goal_type_query = db.query(Goal_Type).first()
        if goal_type_query is None:
            if goal_types:
                for goal_type in goal_types:
                    new_goal_type = Goal_Type(**goal_type)
                    db.add(new_goal_type)
            db.commit()
    except Exception as e:
        logging.warning(e)


def populate_database():
    populate_exercise_type(exercise_type_data)
    populate_exercise_unit(exercise_unit_types)
    populate_goal_type(goal_types)
    populate_exercise(exercises_data)


