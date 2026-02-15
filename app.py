
from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Project

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Use PostgreSQL later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():db.create_all()  # Creates tables if they don't exist

from sqlalchemy.exc import IntegrityError

@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        id_number = request.form.get("id_number")
        name = request.form.get("name")
        phone = request.form.get("phone")
        sublocation = request.form.get("sublocation")

        # Check missing fields
        if not id_number or not name or not phone or not sublocation:
            message = "All fields are required"
            return render_template("register.html", message=message)

        # 🔍 Check if ID already exists
        existing_user = User.query.filter_by(id_number=id_number).first()
        if existing_user:
            message = "Account exist"
            return render_template("register.html", message=message)

        # ✅ Save only if ID does not exist
        new_user = User(
            id_number=id_number,
            name=name,
            phone=phone,
            sublocation=sublocation
        )

        db.session.add(new_user)
        db.session.commit()


        message = "succesufully registered"
        return render_template("register.html", message=message)

    # GET request
    return render_template("register.html", message=message)




@app.route("/submit_project", methods=["GET", "POST"])
def submit_project():
    message = None

    if request.method == "POST":
        id_number = request.form.get("id_number")
        project_name = request.form.get("project_name")
        description = request.form.get("description")
        location = request.form.get("location")

        # 1️⃣ Check if all fields are filled
        if not id_number or not project_name or not description or not location:
            message = "All fields are required"
            return render_template("submit_project.html", message=message)

        # 2️⃣ Check if user is registered
        user = User.query.filter_by(id_number=id_number).first()
        if not user:
            message = "Kindly register first"
            return render_template("submit_project.html", message=message)

        # 3️⃣ Save the project
        new_project = Project(
            user_id=user.id,
            project_name=project_name,
            description=description,
            location=location,
            status="Pending"
        )

        db.session.add(new_project)
        db.session.commit()

        message = "Project submitted successfully"
        return render_template("submit_project.html", message=message)

    # GET request
    return render_template("submit_project.html", message=message)




@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":

        # 🔹 Handle deletion
        if "delete_selected" in request.form:
            selected_ids = request.form.getlist("project_ids")
            for pid in selected_ids:
                project = Project.query.get(pid)
                if project:
                    db.session.delete(project)
            db.session.commit()
            return redirect(url_for("admin"))

        # 🔹 Handle approval
        if "approve_selected" in request.form:
            selected_ids = request.form.getlist("project_ids")
            for pid in selected_ids:
                project = Project.query.get(pid)
                if project:
                    project.status = "Approved"
            db.session.commit()
            return redirect(url_for("admin"))

    projects = Project.query.all()
    return render_template("admin.html", projects=projects)


@app.route("/")
def dashboard():
    total_users = User.query.count()
    total_projects = Project.query.count()
    pending_projects = Project.query.filter_by(status="Pending").count()
    approved_projects = Project.query.filter_by(status="Approved").count()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_projects=total_projects,
        pending_projects=pending_projects,
        approved_projects=approved_projects
    )
@app.route("/pending_projects")
def pending_projects():
    projects = Project.query.filter_by(status="Pending").all()
    return render_template("pending_projects.html", projects=projects)
@app.route("/approved_projects")
def approved_projects():
    projects = Project.query.filter_by(status="Approved").all()
    return render_template("approved_projects.html", projects=projects)


@app.route("/members", methods=["GET", "POST"])
def view_members():
    if request.method == "POST":
        selected_ids = request.form.getlist("delete_ids")

        if selected_ids:
            for user_id in selected_ids:
                user = User.query.get(user_id)
                if user:
                    db.session.delete(user)
            db.session.commit()

        return redirect(url_for("view_members"))

    users = User.query.all()
    return render_template("members.html", users=users)
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    message = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Hard-coded admin credentials (can be changed later)
        ADMIN_USERNAME = "Muga"
        ADMIN_PASSWORD = "6002"

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
           
            return redirect(url_for("admin"))
        else:
            message = "Invalid username or password"

    return render_template("admin_login.html", message=message)






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
