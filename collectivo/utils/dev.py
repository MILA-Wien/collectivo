"""Development helpers."""

# Usernames for test data
DEV_MEMBERS = ["superuser"] + [f"member_{str(i).zfill(2)}" for i in range(5)]
DEV_USERS = DEV_MEMBERS + ["user_not_member", "user_not_verified"]
