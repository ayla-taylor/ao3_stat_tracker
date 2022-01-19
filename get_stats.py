from datetime import datetime
import json
import os

import pandas as pd

import ao3_stats_api


def make_excel(username):
    print("Creating Charts...")
    in_file = "stats_" + username + ".json"
    with open(in_file, 'r') as f:
        data = json.load(f)
    user_stats = {}
    story_dfs = []
    for date in data.keys():
        user_stats[date] = data[date][0]
    user_df = pd.DataFrame.from_dict(user_stats)
    for story in data[date][1]:
        print(story)
        story_stats = {}
        for date in data.keys():
            if data[date][1][story]:
                story_stats[date] = data[date][1][story]
        story_dfs.append((story, pd.DataFrame.from_dict(story_stats)))
    outfile = "AO3_Stats_" + username + ".xlsx"
    print(f"Printing to Excel file \'{outfile}\'...")
    with pd.ExcelWriter(outfile) as writer:
        user_df.to_excel(writer, sheet_name='User Stats')
        for title, story in story_dfs:
            story.to_excel(writer, sheet_name=title)


def get_stats():
    username = input("Username: ")
    password = input("Password: ")
    print("Accessing your AO3 account and pulling your stats...")
    session = ao3_stats_api.Session(username, password)
    today = datetime.now().date()

    print("Updating stats file...")
    filename = "stats_" + username + ".json"
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            stats_dict = json.load(f)
            stats_dict[str(today)] = session.get_statistics()
    else:
        stats_dict = {str(today): session.get_statistics()}
    with open(filename, 'w') as json_file:
        json.dump(stats_dict, json_file)
    # stats_json = json.dumps(stats_dict, indent=4, sort_keys=True)
    # print(stats_json)
    make_excel(username)


if __name__ == '__main__':
    get_stats()
