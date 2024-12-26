def analyze_user_behavior(log_file):
    print(f"Analyzing user behavior in: {log_file}")
    user_attempts = {}

    with open(log_file, "r") as f:
        for line in f:
            if "login attempt" in line:
                user = line.split(":")[1].strip()
                user_attempts[user] = user_attempts.get(user, 0) + 1

    for user, attempts in user_attempts.items():
        if attempts > 3:  # Example threshold
            print(f"Anomaly detected for user {user}: {attempts} login attempts")


