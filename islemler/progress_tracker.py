import time

def show_backup_progress():
    print("Backup in progress...")
    for i in range(1, 101):
        time.sleep(0.1)  # Simulate progress
        print(f"Progress: {i}%", end="\r")
    print("Backup completed!")


