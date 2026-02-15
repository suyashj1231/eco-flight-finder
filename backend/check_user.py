from sqlalchemy.orm import Session
import database, models

def check_user(username):
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            print(f"User '{username}' found!")
            print(f"ID: {user.id}")
            print(f"Hashed Password: {user.hashed_password}")
        else:
            print(f"User '{username}' NOT found.")
    finally:
        db.close()

def list_users():
    db = database.SessionLocal()
    try:
        users = db.query(models.User).all()
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"- {user.username} (ID: {user.id})")
        else:
            print("No users found in database.")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_user(sys.argv[1])
    else:
        list_users()
