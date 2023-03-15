import requests
from jinja2 import Template
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import pandas as pd

# данные для запросов
url = "http://94.79.54.21:3000/"
eduEmail = "gvsivov@edu.hse.ru"
miemEmail = "gvsivov@miem.hse.ru"
beginDate = "2022-01-01"
endDate = "2022-04-01"
beginTime = "10:00:00.000"
endTime = "21:00:00.000"
token = "dIlUIIpKrjCcrmmM"

date_now = datetime.now().isoformat()


# Работа с GitLab
def gitlab():
    git_js = requests.post(url + "api/git/getDataPerWeek", json={
        "studEmail": eduEmail,
        "beginDate": beginDate,
        "endDate": endDate,
        "hideMerge": False,
        "token": token
    }
                            ).json()

    git_project_commits = 0
    git_project_week_all_commits = []
    git_project_dates = []
    git_project_week_commits = []

    sum = 0
    for index in git_js['projects']:
        if index["name"][:17] == "ivt21-miniproject":
            git_project_commits = index['commitCount']
            for index1 in index['commits_stats']:
                date_week = index1['beginDate']
                git_project_dates.append(date_week[:date_week.index('00:00:00')])
                git_project_week_commits.append(index1['commitCount'])
                sum += index1['commitCount']
                git_project_week_all_commits.append(sum)
    
    gitlab_project_gist = go.Figure([go.Bar(x=git_project_dates, y=git_project_week_commits)])
    gitlab_project_graph = go.Figure([go.Scatter(x=git_project_dates, y=git_project_week_all_commits)])

    return git_project_commits, gitlab_project_gist, gitlab_project_graph

# работа с Zulip

def zulip():
    zulip_js = requests.post(url + "api/zulip/getData", json={
        "studEmail": miemEmail,
        "beginDate": beginDate,
        "endDate": endDate,
        "timeRange": 1,
        "token": token
        }).json()

    zulip_messages = len(zulip_js['messages'])
    zulip_channels = []
    zulip_all_messages_per_day = []
    zulip_dates = []
    zulip_messages_per_day = []
    sum = 0

    for index in zulip_js['messages']:
        if not index['name'] in zulip_channels:
            zulip_channels.append(index['name'])
    zulip_channels = ", ".join(zulip_channels)

    for index in zulip_js['stats']:
        date_day = index['beginDate']
        zulip_dates.append(date_day[:date_day.index('00:00:00')])
        zulip_messages_per_day.append(index['messageCount'])
        sum += index['messageCount']
        zulip_all_messages_per_day.append(sum)

    zulip_gist = go.Figure([go.Bar(x=zulip_dates, y=zulip_messages_per_day)])
    zulip_graph = go.Figure([go.Scatter(x=zulip_dates, y=zulip_all_messages_per_day)])

    return zulip_messages, zulip_channels, zulip_gist, zulip_graph

# Работа с Jitsi
def jitsi():
    jitsi_rooms = []
    jitsi_meetings = 0
    jitsi_days = pd.date_range(datetime(2021, 9, 1), datetime(2022, 4, 1)).strftime('%Y-%m-%d').tolist()
    jitsi_dir = {}
    jitsi_all_meetings = {}
    for day in jitsi_days:
        jitsi_dir.update({day: 0})
    
    jitsi_js = requests.post(url + "api/jitsi/sessions", json={
        "studEmail": eduEmail,
        "beginDate": '2021-09-01 ',
        "endDate": endDate,
        "token": token
    }
                            ).json()
    jitsi_meetings += len(jitsi_js)
    sum = 0
    for index in jitsi_js:
        if not index['room'] in jitsi_rooms:
            jitsi_rooms.append(index['room'])
        sum += 1
        jitsi_dir.update({index['date']: jitsi_dir.get(index['date']) + 1})
        jitsi_all_meetings.update({index['date']: sum})
    
    jitsi_rooms = ', '.join(jitsi_rooms)
    jitsi_gist = go.Figure([go.Bar(x=list(jitsi_dir.keys()), y=list(jitsi_dir.values()))])
    jitsi_graph = go.Figure([go.Scatter(x=list(jitsi_all_meetings.keys()), y=list(jitsi_all_meetings.values()))])

    jitsi_pr_meetings = 0
    jitsi_pr_days = pd.date_range(datetime(2022, 1, 1), datetime(2022, 4, 1)).strftime('%Y-%m-%d').tolist()
    jitsi_pr_dir = {}
    jitsi_pr_all_meetings = {}
    for day in jitsi_pr_days:
        jitsi_pr_dir.update({day: 0})

    sum = 0
    sem_rooms = ['ps1', 'ps']
    for room in sem_rooms:
        jitsi_pr_js = requests.post(url + "api/jitsi/sessions", json={
            "studEmail": eduEmail,
            "beginDate": beginDate,
            "endDate": endDate,
            'room': room,
            "token": token
        }
                                    ).json()
        jitsi_pr_meetings += len(jitsi_pr_js)
        for index in jitsi_pr_js:
            sum += 1
            jitsi_pr_dir.update({index['date']: jitsi_pr_dir.get(index['date']) + 1})
            jitsi_pr_all_meetings.update({index['date']: sum})

    jitsi_pr_gist = go.Figure([go.Bar(x=list(jitsi_pr_dir.keys()), y=list(jitsi_pr_dir.values()))])
    jitsi_pr_graph = go.Figure([go.Scatter(x=list(jitsi_pr_all_meetings.keys()), y=list(jitsi_pr_all_meetings.values()))])

    return jitsi_meetings, jitsi_rooms, jitsi_gist, jitsi_graph, jitsi_pr_meetings, jitsi_pr_gist, jitsi_pr_graph


# работа с тайгой
def taiga():
    taiga_dates = []
    my_id = []
    taiga_tasks_array = []
    taiga_userstories = 0
    taiga_tasks = 0

    taiga_js = requests.get("https://track.miem.hse.ru/api/v1/userstories", headers={"x-disable-pagination": "true"}).json()
    for index in taiga_js:
        epics = index['epics']
        if not epics is None and epics[0]['subject'] == 'Сивов Георгий':
            taiga_userstories += 1
            my_id.append(index['id'])

    taiga_js_tasks = requests.get("https://track.miem.hse.ru/api/v1/tasks", headers={"x-disable-pagination": "true"}).json()
    for task in taiga_js_tasks:
        info = task['user_story_extra_info']
        if not info is None and info['id'] in my_id:
            taiga_tasks += 1
            taiga_dates.append(task['created_date'])
            taiga_tasks_array.append(taiga_tasks)

    taiga_graph = go.Figure([go.Scatter(x=taiga_dates, y=taiga_tasks_array)])

    return taiga_userstories, taiga_tasks, taiga_graph

gitlab_stats = gitlab()
zulip_stats = zulip()
jitsi_stats = jitsi()
taiga_stats = taiga()

html = open('/home/prsem/gvsivov/gvsivov/template.html', encoding="utf-8").read()
template = Template(html)

with open("/var/www/html/students/gvsivov/gvsivov.html", "w", encoding="utf-8") as res:
    res.write(template.render(
        date=date_now,

        git_project_commits=gitlab_stats[0],
        gitlab_project_gist=gitlab_stats[1].to_html(),
        gitlab_project_graph=gitlab_stats[2].to_html(),

        zulip_messages=zulip_stats[0],
        zulip_channels=zulip_stats[1],
        zulip_gist=zulip_stats[2].to_html(),
        zulip_graph=zulip_stats[3].to_html(),

        jitsi_meetings=jitsi_stats[0],
        jitsi_rooms=jitsi_stats[1],
        jitsi_gist=jitsi_stats[2].to_html(),
        jitsi_graph=jitsi_stats[3].to_html(),
        jitsi_pr_meetings=jitsi_stats[4],
        jitsi_pr_gist=jitsi_stats[5].to_html(),
        jitsi_pr_graph=jitsi_stats[6].to_html(),

        taiga_stories=taiga_stats[0],
        taiga_tasks=taiga_stats[1],
        taiga_graph=taiga_stats[2].to_html()
    )
    )
