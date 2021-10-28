from flask import Flask, render_template, request
from flask_cors import CORS
import multiprocessing, secrets
import hellohell
import git
app = Flask(__name__)
CORS(app)

import os, sys, shutil

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/.."
sys.path.insert(1, THIS_FOLDER)

shutil.rmtree("sessions", ignore_errors=True)
os.system("mkdir sessions")

sessions = {}
terminated = set()

@app.route('/', methods=['POST','GET'])
def index():
    session = secrets.token_hex(64)
    sessions[session] = None
    return render_template('main.html', session=session)


@app.route("/execute", methods=['POST'])
def execute():
    code = request.form['code'].replace("\r", "")
    input_list = request.form["inputs"].replace("\r", "")
    session = request.form["session"]

    if session not in sessions:
      return {"stdout": "The session was invalid! You may need to reload your tab."}

    shutil.rmtree(f"sessions/{session}", ignore_errors=True)
    os.mkdir(f"sessions/{session}")

    with open(f"sessions/{session}/.stdin", "w", encoding="utf-8") as f:
      f.write(input_list)

    with open(f"sessions/{session}/.stdin", "r", encoding="utf-8") as x:
        with open(f"sessions/{session}/.stdout", "w", encoding="utf-8") as y:
            manager = multiprocessing.Manager()
            ret = manager.dict()
            time = 15

            ret[1] = ""
            ret[2] = ""
            sessions[session] = multiprocessing.Process(target=hellohell.execute, args=(code, input_list, ret))
            sessions[session].start()
            sessions[session].join(time)


            if sessions[session].is_alive():
                sessions[session].terminate()
                ret[1] += "\n\n\n" + f"Code timed out after {time} seconds"

            y.write(ret[1])
    with open(f"sessions/{session}/.stdout", "r", encoding="utf-8") as x:
            val = {"stdout": x.read()}
    shutil.rmtree(f"sessions/{session}", ignore_errors=True)
    return val


@app.route('/commit', methods=['POST'])
def webhook():
    if request.method in ["POST"]:
        repo = git.Repo('/home/hellohell/mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Wrong event type', 400
