from flask import Flask, session, request, url_for, redirect, render_template
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

def render(name):
    with open(f"templates/{name}.html", "r") as f:
        return "".join(f)

def not_seen():
    with open("notif.mnf", "r") as f:
        lines = f.readlines()
    with open("notif.mnf", "w") as f:
        for l in lines:
            if l.split("@")[0] == session["username"]:
                f.write(session["username"] + "@\n")
                stat_to_notif = l.split("@")[1:-1]
            else:
                f.write(l)
    return stat_to_notif

def add_not_seen(field):
    with open("notif.mnf", "r") as f:
        lines = f.readlines()
    with open("notif.mnf", "w") as f:
        for l in lines:
            if l.split("@")[0] != session["username"]:
                f.write(l[:-1] + field + "@\n")
            else:
                f.write(l)

def gather_data():
    data = ""
    with open("data.mnf", "r") as f:
        stats_not_seen = not_seen()
        for line in f.readlines():
            stat, bri, yo, theo, eol = line.split("@")
            data += "<tr>"
            if stat in stats_not_seen:
                data += f"<td style=\"background-color: #FFEEDA\"><label>{stat}</label></td>"
            else:
                data += f"<td><label>{stat}</label></td>"
            for name, value in (("Bri", bri), ("Yohann", yo), ("Theo", theo)):
                if name == session["username"]:
                    data += f"<td><label id=\"{stat}@n\" class=\"hidden\">{value}</label>"
                    data += f"<button class=\"v\" id=\"{stat}@v\" onclick=\'send(\"{stat}\", \"v\")\' style=\"float: right;\"></button>"
                    data += f"<button class=\"x\" id=\"{stat}@x\" onclick=\'send(\"{stat}\", \"x\")\' style=\"float: right;\"></button></td>"
                else:
                    data += f"<td><label class=\"hidden\">{value}</label></td>"
            data += "</tr>\n"
    data += ""
    return data

def set_value(name, new_stat, value):
    w = ""
    with open("data.mnf", "r") as f:
        for line in f.readlines():
            stat, bri, yo, theo, eol = line.split("@")
            if stat == new_stat:
                if name == "Bri":
                    bri = value
                elif name == "Yohann":
                    yo = value
                elif name == "Theo":
                    theo = value
            new_line = "@".join((stat, bri, yo, theo, eol))
            w += new_line
    with open("data.mnf", "w") as f:
        f.write(w)

@app.route("/receive", methods=["POST"])
def receive():
    if "username" not in session:
        return "error"
    stat, value = str(request.get_data())[2:-1].split("@")
    set_value(session["username"], stat, value)
    return "ok"

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("name")
    session["username"] = user
    return redirect(url_for("index"))

@app.route("/")
def index():
    if "username" in session:
         return data()
    else:
        return render("select_name")

@app.route("/data")
def data():
    if "username" not in session:
        return index()
    top = render("top")
    data = gather_data()
    bottom = render("bottom")
    return top + data + bottom

def data_sort():
    with open("data.mnf", "r") as f:
        lines = f.readlines()
        lines.sort()
    with open("data.mnf", "w") as f:
        for l in lines:
            l = l[0].capitalize() + l[1:]
            f.write(l)

@app.route("/new_field", methods=["POST"])
def new_field():
    field = request.form.get("new_field")
    field = field[0].capitalize() + field[1:]
    with open("data.mnf", "a") as f:
        f.write(f"{field}@@@@\n")
    add_not_seen(field)
    data_sort()
    return redirect(url_for("data"))