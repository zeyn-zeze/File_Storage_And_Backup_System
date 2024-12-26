def detect_anomalies(log_file):
    print(f"Analyzing anomalies in: {log_file}")
    failed_login_count = 0

    with open(log_file, "r") as f:
        for line in f:
            if "failed login" in line:
                failed_login_count += 1

    if failed_login_count > 3:  # Example threshold
        print("Anomaly detected: Too many failed logins!")
    else:
        print("No anomalies detected.")

