from flask import Blueprint, render_template, request, redirect, session, jsonify,url_for
from datetime import datetime
from bson.objectid import ObjectId
# from app import mongo
from db import mongo
from ast import literal_eval

admin_bp = Blueprint("admin_bp", __name__)

# Hardcoded Admin Credentials
ADMIN_EMAIL = "admin@123"
ADMIN_PASSWORD = "admin"

# ✅ Admin Login Page
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        else:
            return "Invalid Credentials", 401

    return render_template("admin_login.html")

# @admin_bp.route("/dashboard")
# def dashboard():
#     if not session.get("admin_logged_in"):
#         return redirect("/admin/login")

#     elections = mongo.db.elections.find()  # Fetch all elections

#     return render_template("admin_dashboard.html", elections=elections)


@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    elections = mongo.db.elections.find()
    
    now = datetime.now()

    # Categorize elections
    ongoing = []
    upcoming = []
    completed = []

    for election in elections:
        start_time = election["start_time"]
        end_time = election["end_time"]

        # Ensure datetime format
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        # Categorize elections
        if start_time <= now <= end_time:
            ongoing.append(election)
        elif now < start_time:
            upcoming.append(election)
        else:
            completed.append(election)

    return render_template("admin_dashboard.html", ongoing=ongoing, upcoming=upcoming, completed=completed)

# ✅ Admin Logout
@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")

# ✅ Route to Create a New Election
@admin_bp.route("/create_election", methods=["GET", "POST"])
def create_election():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":
        from app import mongo  # Import here to avoid circular import

        name = request.form["name"]
        region = request.form["region"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        try:
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD HH:MM", 400

        election_data = {
            "name": name,
            "region": region,
            "start_time": start_time,
            "end_time": end_time,
            "candidates": []
        }

        mongo.db.elections.insert_one(election_data)
        return redirect("/admin/dashboard")

    return render_template("create_election.html")

# ✅ Route to Add Candidates to an Election
@admin_bp.route("/add_candidate/<election_id>", methods=["GET", "POST"])
def add_candidate(election_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":
        candidate_name = request.form["name"]
        candidate_party = request.form["party"]
        # discription = request.form["discription"]
        # logo = request.files["logo"]
        

        mongo.db.elections.update_one(
            {"_id": ObjectId(election_id)},
            {"$push": {"candidates": {"name": candidate_name, "party": candidate_party}}}
         )



        # mongo.db.elections.update_one(
        #     {"_id": ObjectId(election_id)},
        #     {"$push": {"candidates": {"name": candidate_name, "party": candidate_party,'discription':discription,'logo':logo}}}
        # )

        return redirect("/admin/dashboard")

    return render_template("add_candidate.html", election_id=election_id)





@admin_bp.route("/delete_candidate/<election_id>/<candidate_name>/<candidate_party>")
def delete_candidate(election_id, candidate_name, candidate_party):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))

    # Remove candidate by matching name and party
    mongo.db.elections.update_one(
        {"_id": ObjectId(election_id)},
        {"$pull": {"candidates": {"name": candidate_name, "party": candidate_party}}}
    )

    # flash("Candidate deleted successfully!", "success")
    return redirect(url_for("admin_bp.dashboard"))


@admin_bp.route("/verify_voters")
def verify_voters():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))

    # Fetch unverified voters (verified: False)
    unverified_voters = list(mongo.db.voters.find({"verified": False}))

    return render_template("verify_voters.html", voters=unverified_voters)


@admin_bp.route("/approve_voter/<voter_id>", methods=["POST"])
def approve_voter(voter_id):
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    # Update voter status to verified (True)
    mongo.db.voters.update_one({"_id": ObjectId(voter_id)}, {"$set": {"verified": True}})

    return jsonify({"message": "Voter Verified Successfully"}), 200





# @admin_bp.route("/election_results/<election_id>")
# def election_results(election_id):
#     if not session.get("admin_logged_in"):
#         return redirect("/admin/login")

#     # Aggregate votes to count votes per candidate
#     pipeline = [
#         {"$match": {"election_id": ObjectId(election_id)}},  # Filter votes for this election
#         {"$group": {"_id": "$candidate", "votes": {"$sum": 1}}},  # Group by candidate and count votes
#         {"$sort": {"votes": -1}}  # Sort by vote count in descending order
#     ]
#     results = list(mongo.db.votes.aggregate(pipeline))

#     # Fetch election details
#     election = mongo.db.elections.find_one({"_id": ObjectId(election_id)})

#     return render_template("election_results.html", election=election, results=results)



# @admin_bp.route("/election_results/<election_id>")
# def election_results(election_id):
#     if not session.get("admin_logged_in"):
#         return redirect("/admin/login")

#     # Fetch all votes for the election
#     votes = list(mongo.db.votes.find({"election_id": ObjectId(election_id)}))

#     # Aggregate votes manually
#     results = {}
#     for vote in votes:
#         # Parse the candidate string into a dictionary
#         try:
#             candidate = literal_eval(vote["candidate"])  # Convert string to dictionary
#             candidate_key = (candidate["name"], candidate["party"])  # Use (name, party) as key
#         except (ValueError, KeyError, SyntaxError):
#             continue  # Skip invalid candidate data

#         # Count votes for each candidate
#         if candidate_key in results:
#             results[candidate_key] += 1
#         else:
#             results[candidate_key] = 1

#     # Convert results to a list of dictionaries for the template
#     results_list = [
#         {"name": key[0], "party": key[1], "votes": value}
#         for key, value in results.items()
#     ]

#     # Sort results by vote count (descending)
#     results_list.sort(key=lambda x: x["votes"], reverse=True)

#     # Fetch election details
#     election = mongo.db.elections.find_one({"_id": ObjectId(election_id)})

#     return render_template("election_results.html", election=election, results=results_list)


@admin_bp.route("/delete_election/<election_id>", methods=["POST"])
def delete_election(election_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))

    try:
        # Delete the election by ID
        result = mongo.db.elections.delete_one({"_id": ObjectId(election_id)})

        if result.deleted_count > 0:
            return redirect(url_for("admin_bp.dashboard"))
        else:
            return "Election not found", 404

    except Exception as e:
        return str(e), 500









# @admin_bp.route("/election_results/<election_id>")
# def election_results(election_id):
#     if not session.get("admin_logged_in"):
#         return redirect("/admin/login")

#     # Fetch all votes for the election
#     votes = list(mongo.db.votes.find({"election_id": ObjectId(election_id)}))

#     # Fetch election details to get candidate information
#     election = mongo.db.elections.find_one({"_id": ObjectId(election_id)})

#     if not election:
#         return "Election not found", 404

#     # Map candidates to vote counts
#     results = {candidate["name"]: {"party": candidate["party"], "votes": 0} for candidate in election["candidates"]}

#     for vote in votes:
#         candidate_name = vote.get("candidate_name")
#         if candidate_name in results:
#             results[candidate_name]["votes"] += 1

#     # Convert results to list and sort by votes
#     results_list = [{"name": name, "party": data["party"], "votes": data["votes"]} for name, data in results.items()]
#     results_list.sort(key=lambda x: x["votes"], reverse=True)

#     return render_template("election_results.html", election=election, results=results_list)




@admin_bp.route('/election_results/<election_id>')
def election_results(election_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    election_id = ObjectId(election_id)  # Convert to ObjectId for MongoDB lookup

    # Fetch votes for the given election
    votes = list(mongo.db.votes.find({"election_id": election_id}))

    # Count votes per candidate
    vote_count = {}
    for vote in votes:
        candidate_data = vote.get("candidate")

        # If candidate_data is a dictionary (as a string), convert it back
        if isinstance(candidate_data, str) and candidate_data.startswith("{"):
            candidate_data = eval(candidate_data)  # Convert string to dictionary (or use `json.loads` safely)

        if isinstance(candidate_data, dict):
            candidate_name = candidate_data.get("name", "Unknown")
            candidate_party = candidate_data.get("party", "Independent")
        else:
            candidate_name = candidate_data
            candidate_party = "Independent"  # Default party if not stored

        key = (candidate_name, candidate_party)  # Tuple key (name, party)
        vote_count[key] = vote_count.get(key, 0) + 1  # Count votes

    # Convert data into a list format for Jinja2
    results = [{"name": k[0], "party": k[1], "votes": v} for k, v in vote_count.items()]

    # Fetch election details (optional)
    election = mongo.db.elections.find_one({"_id": election_id})

    return render_template("election_results.html", results=results, election=election)




@admin_bp.route("/deny_verification/<voter_id>", methods=["POST"])
def deny_verification(voter_id):
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Delete the voter from the database
        result = mongo.db.voters.delete_one({"_id": ObjectId(voter_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Voter denied and removed successfully!"}), 200
        else:
            return jsonify({"error": "Voter not found!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500