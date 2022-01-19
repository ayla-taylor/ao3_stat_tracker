from datetime import datetime
import json
import os
import modified_session


def main():
    username = input("Username: ")
    password = input("Password: ")

    print("Accessing your AO3 account and pulling your stats...")
    session = modified_session.Session(username, password)
    today = datetime.now().date()

    # print(stats_dict)
    print("Updating stats file...")
    if os.path.isfile('stats.json'):
        with open('stats.json', 'r') as f:
            stats_dict = json.load(f)
            stats_dict[str(today)] = session.get_statistics()
    else:
        stats_dict = {str(today): session.get_statistics()}
    with open('stats.json', 'w') as json_file:
        json.dump(stats_dict, json_file)
    stats_json = json.dumps(stats_dict, indent=4, sort_keys=True)
    print(stats_json)


if __name__ == '__main__':
    main()
