# spaghetti rat: Lauren Lee, Brianna Tieu, Emerson Gelobter, Nada Hameed SoftDev
# P01: ArRESTed Development
# 2022-12-04
# time spent:

import db
import api
import matching
import messaging

from flask import Flask, redirect, render_template, request, session, url_for

#====================SQL====================#

db.create_users_db()
db.create_profile_db()
db.create_pref_db()
db.create_messaging_db()
db.create_api_db()

#===========================================#

#====================FLASK====================#
app = Flask(__name__)
app.secret_key = "heightorpersonality"

'''
root route, renders the login page
'''
@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    if 'username' in session: #home page rendered if there is a session
        return render_template('home.html', msg="successfully logged in")
    return render_template('login.html')

'''
login route, checks if attempted login matches data in the
database
- if yes --> user goes to home
- if no --> user gets login page with error messages
'''
@app.route("/login", methods =['GET', 'POST'])
def authenticate():
    user = request.form['username']
    passw = request.form['password']
    #print(db.valid_login(user, passw))

    if db.valid_login(user, passw):
        session['username'] = user
        return render_template('home.html', msg = "successfully logged in")
    else:
        return render_template('login.html', msg="login failed")

'''
register route, allows user to create a new account
'''
@app.route("/register", methods=['GET','POST'])
def register_account():
    if request.method == 'GET':
        return render_template('register.html')
    user = request.form['newUser']
    #user = request.form.get('newUser')
    passw = request.form['newPass']
    #passw = request.form.get('newPass')

    if db.user_exists(user):
        return render_template('register.html', msg="username is in use!")
    else:
        db.add_user(user, passw)
        return render_template('login.html', msg = "user registered!, log in with your new credentials.")

@app.route("/logout", methods=['GET', 'POST'])
def log_out():
    session.pop('username', None)
    return redirect('/')

'''
display route, shows users their existing information (if there is any), allows them to edit and submit new information
'''
@app.route("/display", methods=['GET', 'POST'])
def disp_profile():
    if db.get_profile(session['username']) == None and db.get_pref(session['username']) == None:
        #print("\n===========new user==============\n")
        return render_template('profile.html')
    if db.get_profile(session['username']) is not None and db.get_pref(session['username']) == None:
        #print("\n=====================needs pref=================\n")
        profile_data = db.get_profile(session['username'])
        return render_template('profile.html', msg="Complete the preferences form to find matches!", name=profile_data[0], birth=profile_data[1], height=profile_data[2], hobby1=profile_data[3], hobby2=profile_data[4], spotify=profile_data[5], gender=profile_data[6], mbti=profile_data[7])
    if db.get_profile(session['username']) == None and db.get_pref(session['username']) is not None:
        #print("\n=====================needs prof=================\n")
        pref_data = db.get_pref(session['username'])
        return render_template('profile.html', msg="Complete your profile form to find matches!", pref_star=pref_data[0], pref_mbti=pref_data[1], use_star=pref_data[2], use_mbti=pref_data[3], low_height=pref_data[4], high_height=pref_data[5], pref_female=pref_data[6], pref_male=pref_data[7], pref_nonbinary=pref_data[8])
    if db.get_profile(session['username']) is not None and db.get_pref(session['username']) is not None:
        #print("\n============nothing============\n")
        profile_data = db.get_profile(session['username'])
        pref_data = db.get_pref(session['username'])
        return render_template('profile.html', name=profile_data[0], birth=profile_data[1], height=profile_data[2], hobby1=profile_data[3], hobby2=profile_data[4], gender=profile_data[6], mbti=profile_data[7], pref_star=pref_data[0], pref_mbti=pref_data[1], use_star=pref_data[2], use_mbti=pref_data[3], low_height=pref_data[4], high_height=pref_data[5], pref_female=pref_data[6], pref_male=pref_data[7], pref_nonbinary=pref_data[8])

'''
profile route, creates a profile if the user doesn't already have one, updates the newly submitted information if the user does have one, redirects to display route
'''
@app.route("/profile", methods=['GET', 'POST'])
def update_pro():
    user = session['username']
    name = request.form.get('name')
    birthday = request.form.get('birthday')
    height = request.form.get('height')
    hobby_1 = request.form.get('hobby1')
    hobby_2 = request.form.get('hobby2')
    spotify = request.form.get('spotify')
    gender = request.form.get('gender')
    mbti = request.form.get('mbti')
    if request.method == 'POST' and db.get_profile(session['username']) == None:
        db.profile_setup(user, name, birthday, height, hobby_1, hobby_2, spotify, gender, mbti)
    if request.method == 'POST' and db.get_profile(session['username']) is not None:
        db.profile_update(user, name, birthday, height, hobby_1, hobby_2, spotify, gender, mbti)
    return redirect(url_for('disp_profile'))

'''
preferences route, creates a preference profile if the user doesn't already have one, updates the newly submitted information if the user does have one, redirects to display route
'''
@app.route("/preferences", methods=['GET', 'POST'])
def update_pref():
    user = session['username']
    star_sign = request.form.get('pref_star')
    mbti = request.form.get('pref_mbti')
    use_star_sign = request.form.get('use_star')
    use_mbti = request.form.get('use_mbti')
    low_height = request.form.get('low_height')
    high_height = request.form.get('high_height')
    female = request.form.get('pref_female')
    male = request.form.get('pref_male')
    nonbinary = request.form.get('pref_nonbinary')
    if request.method == 'POST' and db.get_pref(session['username']) == None:
        db.pref_setup(user, star_sign, mbti, use_star_sign, use_mbti, low_height, high_height, female, male, nonbinary)
    if request.method == 'POST' and db.get_pref(session['username']) is not None:
        db.pref_update(user, star_sign, mbti, use_star_sign, use_mbti, low_height, high_height, female, male, nonbinary)
    return redirect(url_for('disp_profile'))

'''
match route, calls matching methods and provides the html file with the match information + cute ducky photos to put into cards :)
'''
@app.route("/match", methods=['GET', 'POST'])
def disp_matches():
    matchList = {}
    matches = matching.match(session['username'])
    for match in matches.keys():
        i = matching.get_match_info(match, matches)
        match_name=""
        for letter in i[0]: #turn tuple data into string data to be displayed on match page
            match_name = match_name + letter
        matchList[match_name]=[str(int(i[1]))]
        duck = db.get_duck(match)
        duck_link=""
        for letter in duck[0]: #turn tuple data into link for ducks :)
            duck_link = duck_link + letter
        matchList[match_name].append(duck_link)
        matchList[match_name].append(match)

    return render_template('match.html', matchList = matchList)


@app.route("/match/<username>/answer", methods=['GET', 'POST'])
def disp_ans(username):
    extra_info = []
    more = matching.get_extra_match_info(username)
    print(more)
    for item in more:
            item = str(item)[1:-2]
            extra_info.append(item)
    extra_info[6] = extra_info[6].strip("\'")
    ans = messaging.random_update_api_db(session['username'], username)
    if messaging.check_db(session['username'], username) == True:
        if messaging.can_message(session['username'], username) == False:
            return render_template('no.html', user = username, answer = ans, bday=extra_info[0], star_sign=extra_info[1], mbti=extra_info[2], height=extra_info[3], hobby1=extra_info[4], hobby2=extra_info[5], spotify=extra_info[6])
    if ans == False:
        return render_template('no.html', user = username, answer = ans, bday=extra_info[0], star_sign=extra_info[1], mbti=extra_info[2], height=extra_info[3], hobby1=extra_info[4], hobby2=extra_info[5], spotify=extra_info[6])
    if ans == True:
        return render_template('yes.html', user = username, answer = ans, bday=extra_info[0], star_sign=extra_info[1], mbti=extra_info[2], height=extra_info[3], hobby1=extra_info[4], hobby2=extra_info[5], spotify=extra_info[6])

@app.route("/message/<username>", methods=['GET', 'POST'])
def display_message(username):
    if messaging.check_db(session['username'], username) ==  False:
        print("it is false")
        messaging.nonrandom_update_api_db(session['username'], username)
        msg = messaging.get_message(session['username'], username)
        time = messaging.get_time(session['username'], username)
        sender = messaging.get_user(session['username'], username)
        return render_template('message.html', user=username, sender = sender, latest=msg, time=time)
    else: 
        print("true")
       # if db.can_message(session['username'], username) == True:
        msg = messaging.get_message(session['username'], username)
        time = messaging.get_time(session['username'], username)
        sender = messaging.get_user(session['username'], username)
        return render_template('message.html', user=username, sender = sender, latest=msg, time=time)
    # if messaging.can_message(session['username'], username) == False:
    #     return render_template('prevno.html')
    # else:
    #     return render_template('prevno.html')
    # #     #if messaging.get_message(session['username'], username) is not None:
    # #     msg = messaging.get_message(session['username'], username)
    # #     time = messaging.get_time(session['username'], username)
    # #     return render_template('message.html', user=username, messaged=True, latest=msg, time=time)
    # # return render_template('message.html', user=username)

@app.route("/message/<username>/update", methods=['GET', 'POST'])
def update_messages(username):
    if messaging.can_message(session['username'], username):
        msg = request.form.get('msg')
        messaging.send_message(session['username'], username, msg)
        messaging.update_permission(session['username'], username)
        time = messaging.get_time(session['username'], username)
        return render_template('message.html', user=username, sender = session['username'], latest=msg, time=time)
    else:
        return render_template('prevno.html')

@app.errorhandler(500)
def no_info():
    return render_template('nomatchinfo.html'), 500
#================================================#

if __name__ == "__main__":  # true if this file NOT imported
    app.debug = True        # enable auto-reload upon code change
    app.run()
