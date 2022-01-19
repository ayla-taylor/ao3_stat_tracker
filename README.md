# AO3 Stat Tracker

A tool for tracking the statistics of your works on the fanfiction site Archive of Our Own

Motivation for this project: 
On AO3, you can see your cumulative stats but you can't see your stats over time. 
This program is designed so that every time you run it, it pulls all your stats, and adds them to a cumulative JSON file.

---

### Installation: 

To install:  
1. download the directory 
2. using the terminal (see [this tutorial](https://towardsdatascience.com/a-quick-guide-to-using-command-line-terminal-96815b97b955) if you are unfamilar.) access the directory.
3. run the following command: `pip install -r requirements.txt`


### Running the program: 

This program only collects the stats when you run it, and only collects one datapoint for each day. 
Each day you want the stats recorded, you have to run the following command:

`python get_stats.py`

It will then prompt you for your username and password. 

The first time you run the program, it will generate two files (with your username): 
- stats_username.json
- AO3_Stats_username.xlsx

The first file is where the information is stored, but it is not very human readable. 
The second is an Excel file with a tab for your overall user stats and for each of your works. 

Note: The Excel file will update and replace each time you run it, so if you alter the excel file without changing the name, it will be overwritten. 

### Special Thanks:

This was made much easier by the existance of an existing AO3 api, found [here](https://github.com/ArmindoFlores/ao3_api). 


### Future Plans:

I have a few ideas of how to improve this project: 
- I would like to make it more user friendly so it doesn't need to be run from the terminal.
- I would like to add visualizations, rather than just producing an Excel file. 

I am in grad school right now so who knows when I will have time for improving it. If you liked this and want to thank me/motivate me to make it better or make other tools, consider [buying me a coffee](https://ko-fi.com/aylataylor)!
