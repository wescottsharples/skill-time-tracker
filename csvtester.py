#!/usr/bin/env python3
import csv
import json
with open("projects.json", "r") as f:
    projects = json.load(f)
out = open("projects.csv", "w")
writer = csv.writer(out)
project_names = list(projects)

for name in project_names:
    writer.writerow([name])
    writer.writerow(["total time", projects[name]["total"]])
    writer.writerow(["day", "time"])
    days = projects[name]["days"]
    for k, v in days.items():
        writer.writerow([k, v])
