def log(message):
    with open('data/logs.txt', 'a') as f:
        f.write(f"{message}\n")
