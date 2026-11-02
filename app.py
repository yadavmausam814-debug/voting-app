
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "voting_secret_123"

# Data store (simple ke liye memory me)
users = {}  # username: password
votes = {"BJP": 0, "Congress": 0, "AAP": 0}
voted_users = set()

# --- HTML Templates ---

LOGIN_PAGE = """
<!DOCTYPE html><html><head><title>Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.card{background:white;padding:30px;border-radius:15px;width:90%;max-width:350px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}input{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}button{width:100%;padding:12px;background:#1877f2;color:white;border:none;border-radius:8px;font-size:16px;margin-top:10px;cursor:pointer}a{color:#1877f2;text-decoration:none}</style>
</head><body><div class="card"><h2>Login</h2>
<form method="post"><input name="username" placeholder="Username" required><input name="password" type="password" placeholder="Password" required><button>Login</button></form>
<p>Account nahi hai? <a href="/register">Register karo</a></p></div></body></html>
"""

REGISTER_PAGE = """
<!DOCTYPE html><html><head><title>Register</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.card{background:white;padding:30px;border-radius:15px;width:90%;max-width:350px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}input{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}button{width:100%;padding:12px;background:#42b72a;color:white;border:none;border-radius:8px;font-size:16px;margin-top:10px;cursor:pointer}a{color:#1877f2;text-decoration:none}</style>
</head><body><div class="card"><h2>Register</h2>
<form method="post"><input name="username" placeholder="Username banao" required><input name="password" type="password" placeholder="Password banao" required><button>Register</button></form>
<p>Pehle se account hai? <a href="/login">Login karo</a></p></div></body></html>
"""

HOME_PAGE = """
<!DOCTYPE html><html><head><title>Home - Voting</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#f0f2f5;text-align:center;padding:15px;margin:0}.card{background:white;max-width:400px;margin:20px auto;padding:25px;border-radius:15px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}.logout{position:absolute;top:15px;right:15px;background:#ff3b30;color:white;padding:8px 12px;border-radius:6px;text-decoration:none}button{width:100%;padding:14px;margin:10px 0;border:none;border-radius:8px;font-size:17px;cursor:pointer;background:#1877f2;color:white;font-weight:bold}button:disabled{background:#ccc}.result{background:#f7f7f7;padding:10px;border-radius:8px;margin-top:15px}</style>
</head><body>
<a href="/logout" class="logout">Logout</a>
<div class="card">
<h2>Welcome, {{user}}! 👋</h2>
<h1>🗳️ Online Voting</h1>
{% if already_voted %}
<p style="color:green;font-weight:bold">✅ Tum vote kar chuke ho!</p>
{% else %}
<form action="/vote" method="post">
<button type="submit" name="party" value="BJP">BJP ko Vote</button>
<button type="submit" name="party" value="Congress">Congress ko Vote</button>
<button type="submit" name="party" value="AAP">AAP ko Vote</button>
</form>
{% endif %}
<div class="result">
<h3>Live Result</h3>
<p>BJP: {{votes['BJP']}} | Congress: {{votes['Congress']}} | AAP: {{votes['AAP']}}</p>
<p><b>Total Votes: {{total}}</b></p>
</div>
</div></body></html>
"""

@app.route("/")
def home():
    if 'user' not in session: return redirect("/login")
    return render_template_string(HOME_PAGE, user=session['user'], votes=votes, total=sum(votes.values()), already_voted=session['user'] in voted_users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username"); p = request.form.get("password")
        if u in users and users[u] == p:
            session['user'] = u
            return redirect("/")
        return "Galat username/password! <a href='/login'>Wapas jao</a>"
    return LOGIN_PAGE

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username"); p = request.form.get("password")
        if u in users: return "User pehle se hai! <a href='/register'>Wapas</a>"
        users[u] = p
        return redirect("/login")
    return REGISTER_PAGE

@app.route("/vote", methods=["POST"])
def vote():
    if 'user' not in session: return redirect("/login")
    if session['user'] in voted_users: return redirect("/")
    party = request.form.get("party")
    if party in votes:
        votes[party] += 1
        voted_users.add(session['user'])
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/login")

if __name__ == '__main__':
    run_with_cloudflared(app)
    app.run(port=5000)
    
