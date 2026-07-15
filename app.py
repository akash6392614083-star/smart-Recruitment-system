from flask import Flask, render_template,request,redirect,url_for,flash,session
import mysql.connector
import pickle

model = pickle.load(open("model.pkl", "rb"))


app = Flask(__name__)
app.secret_key="smarthire123"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/candidate")
def candidate():
    return render_template("candidate.html")

@app.route("/recruiter")
def recruiter():
    return render_template("recruiter.html")


db=mysql.connector.connect(
    host='127.0.0.1',
    user="root",
    password="akash2005",
    database="smart_recruitment"
    
    
)

cursor=db.cursor()
@app.route("/candidate/register",methods=['GET','POST'])
def candidate_register():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        phone=request.form['phone']
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already exists! Please use another email.", "danger")
            return render_template("candidate.html", active_tab="register")
        cursor.execute(
            "insert into users(name,email,password,role,phone) values(%s,%s,%s,%s,%s)",(name,email,password,"candidate",phone)
            
        )
        db.commit()
        flash("Account Created Successfully! Please Login","success")
        # return redirect(url_for("candidate"))
    return render_template ("candidate.html",active_tab="register")

@app.route("/recruiter/register",methods=['GET','POST'])
def recruiter_register():
    if request.method=='POST':
        name=request.form['name']
        company_name=request.form['company_name']
        email=request.form['email']
        phone=request.form['phone']
        location=request.form['location']
        password=request.form['password']
        
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already exists! Please use another email.", "danger")
            return render_template("recruiter.html", active_tab="register")
        
        cursor.execute("""insert into users(name,email,password,role,phone)
                      values(%s,%s,%s,%s,%s)""",(name,email,password,"Recruiter",phone))
        user_id=cursor.lastrowid
        cursor.execute("""
                       insert into recruiters(user_id,company_name,company_email,phone_number,location,name)
                       values(%s,%s,%s,%s,%s,%s) """,
                       (user_id,company_name,email,phone,location,name))
        
        db.commit()
        
        flash("Account Created Successfully! Please Login","success")
        # return redirect(url_for("candidate"))
    return render_template ("recruiter.html",active_tab="register")

@app.route("/candidate/login", methods=["POST"])
def candidate_login():
    email = request.form["email"]
    password = request.form["password"]

    cursor.execute("""
        SELECT * FROM users
        WHERE email=%s AND password=%s AND role='candidate'
    """, (email, password))

    user = cursor.fetchone()

    if user:

        session["user_id"] = user[0]
        session["role"] = "candidate"

        flash("Login Successful!", "success")
        return redirect(url_for("candidate_dashboard"))

    else:

        flash("Invalid Email or Password!", "danger")
        return render_template("candidate.html", active_tab="login")
    
    
@app.route("/recruiter/login", methods=["POST"])
def recruiter_login():
    email = request.form["email"]
    password = request.form["password"]

    cursor.execute("""
        SELECT * FROM users
        WHERE email=%s AND password=%s AND role='Recruiter'
    """, (email, password))

    user = cursor.fetchone()

    if user:

        # Save recruiter session
        session["user_id"] = user[0]
        session["role"] = "Recruiter"

        # flash("Login Successful!", "success")
        return redirect(url_for("recruiter_dashboard"))

    else:
        flash("Invalid Email or Password!", "danger")
        return render_template("recruiter.html", active_tab="login")
@app.route("/candidate/dashboard")
def candidate_dashboard():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    return render_template("candidate_dashboard.html")
    
@app.route("/browse-jobs")
def browse_jobs():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    return render_template("browse_jobs.html", jobs=jobs)

@app.route("/my-applications")
def my_applications():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    user_id = session["user_id"]

    # Get candidate id
    cursor.execute("""
        SELECT candidate_id
        FROM candidate
        WHERE user_id=%s
    """, (user_id,))

    candidate = cursor.fetchone()

    if not candidate:
        flash("Candidate profile not found", "danger")
        return redirect(url_for("candidate_dashboard"))

    candidate_id = candidate[0]

    # Fetch applied jobs
    cursor.execute("""
        SELECT 
            jobs.job_titile,
            jobs.location,
            jobs.salary,
            application.application_date,
            application.status,
            application.prediction
        FROM application
        JOIN jobs
        ON application.job_id = jobs.job_id
        WHERE application.candidate_id=%s
    """, (candidate_id,))

    applications = cursor.fetchall()

    return render_template(
        "my_applications.html",
        applications=applications
    )
@app.route("/my-profile")
def my_profile():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    user_id = session["user_id"]

    cursor.execute("""
        SELECT
            users.name,
            users.email,
            users.phone,
            candidate.cgpa,
            candidate.aptitude_score,
            candidate.communication_score,
            candidate.skill,
            candidate.internship,
            candidate.projects,
            candidate.resume
        FROM users
        JOIN candidate
        ON users.user_id = candidate.user_id
        WHERE users.user_id=%s
    """, (user_id,))

    profile = cursor.fetchone()

    return render_template(
        "my_profile.html",
        profile=profile
    )
    
@app.route("/update-profile", methods=["POST"])
def update_profile():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    user_id = session["user_id"]

    internship = request.form["internship"]
    projects = request.form["projects"]

    cursor.execute("""
        UPDATE candidate
        SET internship=%s,
            projects=%s
        WHERE user_id=%s
    """, (internship, projects, user_id))

    db.commit()

    flash("Profile Updated Successfully!", "success")

    return redirect(url_for("my_profile"))

@app.route("/create-profile", methods=["GET","POST"])
def create_profile():

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    if request.method == "POST":

        user_id = session["user_id"]

        cursor.execute("""
        INSERT INTO candidate
        (
            user_id,
            cgpa,
            aptitude_score,
            communication_score,
            skill,
            internship,
            projects
            
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            user_id,
            request.form["cgpa"],
            request.form["aptitude_score"],
            request.form["communication_score"],
            request.form["skill"],
            request.form["internship"],
            request.form["projects"]
            
        ))

        db.commit()

        return redirect(url_for("my_profile"))

    return render_template("create_profile.html")
    
    
    
@app.route("/recruiter/dashboard")
def recruiter_dashboard():
    return render_template("recruiter_dashboard.html")

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    # Check if recruiter is logged in
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("recruiter"))

    if request.method == "POST":

        # Logged-in user's ID
        user_id = session["user_id"]

        # Get recruiter_id from recruiters table
        cursor.execute("""
            SELECT recruiter_id
            FROM recruiters
            WHERE user_id = %s
        """, (user_id,))

        recruiter = cursor.fetchone()

        if recruiter is None:
            flash("Recruiter not found!", "danger")
            return redirect(url_for("recruiter_dashboard"))

        recruiter_id = recruiter[0]

        # Get form data
        job_title = request.form["job_title"]
        job_description = request.form["job_description"]
        required_skill = request.form["required_skill"]
        minimum_cgpa = request.form["minimum_cgpa"]
        salary = request.form["salary"]
        location = request.form["location"]
        last_date = request.form["last_date"]

        # Insert job
        cursor.execute("""
            INSERT INTO jobs
            (
                recruiter_id,
                job_titile,
                job_description,
                required_skill,
                minimum_cgpa,
                salary,
                location,
                last_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            recruiter_id,
            job_title,
            job_description,
            required_skill,
            minimum_cgpa,
            salary,
            location,
            last_date
        ))

        db.commit()

        flash("Job Posted Successfully!", "success")

        return redirect(url_for("my_jobs"))

    return render_template("post_job.html")

# @app.route("/candidate/dashboard")
# def candidate_dashboard():
#     return render_template("candidate_dashboard.html")

@app.route("/apply-job/<int:job_id>")
def apply_job(job_id):

    if "user_id" not in session:
        return redirect(url_for("candidate"))

    user_id = session["user_id"]
    print("Logged in user:", user_id)

    cursor.execute("""
        SELECT candidate_id
        FROM candidate
        WHERE user_id=%s
    """, (user_id,))

    candidate = cursor.fetchone()

    if not candidate:
        flash("Candidate profile not found.", "danger")
        return redirect(url_for("candidate_dashboard"))

    candidate_id = candidate[0]

    cursor.execute("""
        SELECT *
        FROM application
        WHERE candidate_id=%s AND job_id=%s
    """, (candidate_id, job_id))

    already = cursor.fetchone()

    if already:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("candidate_dashboard"))

    cursor.execute("""
        INSERT INTO application
        (candidate_id, job_id, prediction, status)
        VALUES(%s, %s, %s, %s)
    """, (candidate_id, job_id, None, "pending"))

    db.commit()

    flash("Application Submitted Successfully!", "success")

    return redirect(url_for("candidate_dashboard"))
@app.route("/my-jobs")
def my_jobs():

    if "user_id" not in session:
        return redirect(url_for("recruiter"))

    user_id = session["user_id"]

    # Get recruiter_id
    cursor.execute("""
        SELECT recruiter_id
        FROM recruiters
        WHERE user_id=%s
    """, (user_id,))

    recruiter = cursor.fetchone()

    if recruiter is None:
        flash("Recruiter not found.", "danger")
        return redirect(url_for("recruiter_dashboard"))

    recruiter_id = recruiter[0]

    cursor.execute("""
        SELECT
            job_id,
            job_titile,
            location,
            salary,
            last_date
        FROM jobs
        WHERE recruiter_id=%s
    """, (recruiter_id,))

    jobs = cursor.fetchall()

    return render_template("my_jobs.html", jobs=jobs)

@app.route("/view-applicants/<int:job_id>")
def view_applicants(job_id):

    if "user_id" not in session:
        return redirect(url_for("recruiter"))

    cursor.execute("""
        SELECT
            application.application_id,
            users.name,
            users.email,
            users.phone,
            candidate.cgpa,
            candidate.aptitude_score,
            candidate.communication_score,
            candidate.skill,
            candidate.internship,
            candidate.projects,
            application.status,
            application.prediction
        FROM application
        JOIN candidate
            ON application.candidate_id = candidate.candidate_id
        JOIN users
            ON candidate.user_id = users.user_id
        WHERE application.job_id = %s
    """, (job_id,))

    applicants = cursor.fetchall()

    return render_template(
        "view_applicants.html",
        applicants=applicants,
        job_id=job_id
    )
@app.route("/ai-shortlisting")
def ai_shortlisting():

    print("AI Shortlisting route called")

    if "user_id" not in session:
        return redirect(url_for("recruiter"))

    user_id = session["user_id"]

    cursor.execute("""
    SELECT recruiter_id
    FROM recruiters
    WHERE user_id=%s
    """, (user_id,))

    recruiter = cursor.fetchone()

    if recruiter is None:
        flash("Recruiter not found!")
        return redirect(url_for("recruiter_dashboard"))

    recruiter_id = recruiter[0]

    cursor.execute("""
        SELECT
            application.application_id,
            candidate.cgpa,
            candidate.aptitude_score,
            candidate.communication_score,
            candidate.skill,
            candidate.internship,
            candidate.projects
        FROM application
        INNER JOIN candidate
            ON application.candidate_id = candidate.candidate_id
        INNER JOIN jobs
            ON application.job_id = jobs.job_id
        WHERE jobs.recruiter_id = %s
    """, (recruiter_id,))

    applicants = cursor.fetchall()
    print(applicants)

    print(applicants)   # Debugging

    for applicant in applicants:

        application_id = applicant[0]

        features = [[
            float(applicant[1]),   # CGPA
            int(applicant[2]),     # Aptitude
            int(applicant[3]),     # Communication
            int(applicant[4]),     # Skill
            int(applicant[5]),     # Internship
            int(applicant[6])      # Projects
        ]]

        prediction = model.predict(features)[0]

        if prediction == 1:
            result = "Shortlisted"
        else:
            result = "Not Shortlisted"

        cursor.execute("""
            UPDATE application
            SET prediction = %s
            WHERE application_id = %s
        """, (result, application_id))

    db.commit()

    # flash("AI Shortlisting completed successfully!")

    return redirect(url_for("my_jobs"))



if __name__ == "__main__":
    app.run(debug=True)