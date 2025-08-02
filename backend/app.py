from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text, desc
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import traceback
from sqlalchemy import or_
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from cryptography.fernet import Fernet

# Load .env file contents into environment variables
load_dotenv()

from __init__ import app
from __init__ import db
key = os.getenv("FERNET_KEY").encode() 
f = Fernet(key)

cloudinary.config( 
    cloud_name = os.getenv("CLOUD_NAME"), 
    api_key = os.getenv("CLOUD_API_KEY"), 
    api_secret = os.getenv("API_SECRET"),
    secure=True
)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, Profile, Friends, Friend_Requests, Groups, GroupRequests, GroupMembers, Posts, Messages

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    try:
        db.session.execute(text("SELECT 1"))
        print("✅ Connected to database.")
    except Exception as e:
        print("❌ Failed to connect:", e)

# SPLASH PAGE:
@app.route('/', methods=['GET', 'POST'])
def splash():
    return render_template('splash.html')

# LOGIN/REGISTER:
@app.route('/register', methods=['GET', 'POST'])
def register():
    invalid = False
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            invalid = True
            message = "Email already registered"
            print("email already registered")
            return render_template('register.html', invalid = invalid, flag = message)

        # Hash the password
        hashed_password = generate_password_hash(password)
        print(hashed_password)

        # Create new user
        new_user = User(username = username, name=name, email=email, password=hashed_password, avatar_url = 'img/default_avatar.png')

        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    invalid = False
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = User.query.filter_by(email=email).first()
        if users and check_password_hash(users.password, password):
            print(users.email, users.name)
            login_user(users)
            print("success")
            if users.first_login == False:
                users.first_login = True;
                db.session.commit()
                return redirect(url_for('createProfile'))
            return redirect(url_for('dash'))  # Or wherever you want to redirect
        else:
            invalid = True
            message = 'Invalid email or password.'
            print("failed login")

    return render_template('login.html', invalid = invalid, flag = message)

# DASHBOARD:
def time_since(time_input):
    mst = ZoneInfo("America/Denver")
    now = datetime.now(mst)

    # If `time_input` is naive, localize it to MST
    if time_input.tzinfo is None:
        time_input = time_input.replace(tzinfo=mst)
    else:
        time_input = time_input.astimezone(mst)
    diff = now - time_input
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    
    if seconds < 60:
        return "less than 1 min"
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    elif days < 7:
        return f"{int(days)} days ago"
    else:
        return time_input.strftime("%b %d, %Y")
    
    
    
    

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dash():
    # get all posts where group_id is a group current user is in, or creator_id is a friend of current user.
    if request.method == 'GET':
        friends = Friends.query.filter((Friends.user1_id == current_user.user_id)|(Friends.user2_id == current_user.user_id)).all()
        friend_ids = []
        for friend in friends:
            if friend.user1_id == current_user.user_id:
                friend_ids.append(friend.user2_id)
            else:
                friend_ids.append(friend.user1_id)
        groups = GroupMembers.query.filter(GroupMembers.user_id == current_user.user_id).all()
        group_ids = []
        for group in groups:
            group_ids.append(group.group_id)
        posts = Posts.query.filter(or_(
            Posts.creator_id.in_(friend_ids),
            Posts.group_id.in_(group_ids)
        )).order_by(desc(Posts.time_posted))
        dash_posts = []
        for post in posts:
            group = Groups.query.filter(Groups.group_id == post.group_id).first()
            user = User.query.filter(User.user_id == post.creator_id).first()
            timestamp = time_since(post.time_posted)
            owner = False
            if post.creator_id == current_user.user_id:
                owner = True
            elif group.creator_id == current_user.user_id:
                owner = True
                
            dash_posts.append({'post': post, 'group': group, 'creator': user, 'timestamp': timestamp, 'owner': owner})
        
        return render_template('dashboard.html', user = current_user.name, avatar_url = current_user.avatar_url, user_id = current_user.user_id, dash_posts = dash_posts)
    return render_template('dashboard.html', user = current_user.name, avatar_url = current_user.avatar_url, user_id = current_user.user_id)

@app.route('/dashboard/post', methods=['GET', 'POST'])
@login_required
def createPost():
    if request.method == 'POST':
        caption = request.form['caption']
        group_id = request.form['group_id']
        file = request.files['image_file']
        url = upload_avatar_to_cloudinary(file, current_user.user_id)
        
        new_post = Posts(creator_id = current_user.user_id, content = caption, image_url = url, group_id = group_id)
        
        db.session.add(new_post)
        db.session.commit()
        
        post_ret = Posts.query.filter_by(content = caption).first()
        if post_ret.post_id:
            print("Post created!")
        else:
            print("Error")
        
        return redirect(url_for('dash'))
    return redirect(url_for('dash'))

@app.route('/dashboard/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def deletePost(id):
    post = Posts.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
    else:
        print("post not found")
        
    return redirect(url_for('dash'))
    
@app.route('/dashboard/search_joined_groups', methods=['GET'])
@login_required
def search_joined_groups():
    query = request.args.get('groupId', '').strip()
    if len(query) < 2:
        # Return empty list if query too short (matches your JS condition)
        return jsonify([])

    # Query groups where current_user is a member AND group name matches query (case-insensitive)
    results = (
        Groups.query
        .join(GroupMembers, Groups.group_id == GroupMembers.group_id)
        .filter(
            GroupMembers.user_id == current_user.user_id,
            Groups.name.ilike(f"%{query}%")
        )
        .limit(10)
        .all()
    )

    groups = [{'id': group.group_id, 'name': group.name} for group in results]
    return jsonify(groups)
    

# IMAGE UPLOAD:
ALLOWED_EXTENSIONS = ['png', 'jpeg', 'jpg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_avatar_to_cloudinary(_file, user_id):
    if _file and allowed_file(_file.filename):
        filename = secure_filename(_file.filename)
        
        # Upload directly to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                _file,
                folder="avatars",  # optional folder
                public_id=f"user_{user_id}_{filename.rsplit('.', 1)[0]}",
                overwrite=True,
                resource_type="image"
            )
            print("Upload success:", upload_result['secure_url'])
            return upload_result['secure_url']
        except Exception as e:
            print("Cloudinary upload error:", e)
            return None
        
# PROFILE:
@app.route('/createProfile', methods=['GET', 'POST'])
@login_required
def createProfile():
    
    existing_profile = Profile.query.filter_by(user_id=current_user.user_id).first()
    existing_avatar_url = existing_profile.avatar_url if existing_profile else None
    
    if request.method == 'POST':
        bio = request.form['bio']
        location = request.form['location']
        status = request.form['user_type']
        interests = request.form.getlist('interests[]')
        conditions = request.form.getlist('conditions[]')
        private = request.form.get('private') == 'on'
        print(private)
        file = request.files['avatar_file']
        url = upload_avatar_to_cloudinary(file, current_user.user_id)
        print(url)
        if existing_profile:
            existing_profile.bio = bio
            existing_profile.location = location
            existing_profile.status = status
            existing_profile.interests = interests
            existing_profile.conditions = conditions
            existing_profile.private = private
            if file and file.filename != '':
                existing_profile.avatar_url = url
                current_user.avatar_url = url
            else:
                existing_profile.avatar_url= existing_avatar_url
                current_user.avatar_url = existing_avatar_url
            
        else: 
            new_profile = Profile(
                user_id = current_user.user_id, 
                bio = bio, status = status, 
                location = location, 
                interests = interests, 
                conditions = conditions, 
                private = private,
                avatar_url = url)
            db.session.add(new_profile)
            current_user.avatar_url = url
        db.session.commit()
        
        print("Profile Created!")
        return redirect(url_for('showProfile', id = current_user.user_id))
    
    elif request.method == "GET":
        if existing_profile:
            return render_template('createProfile.html', name = current_user.name, bio = existing_profile.bio, status = existing_profile.status, location = existing_profile.location, interests = existing_profile.interests, conditions = existing_profile.conditions, avatar_url = current_user.avatar_url, private = existing_profile.private, user_id = current_user.user_id)
        else:
            return render_template('createProfile.html', user_id = current_user.user_id)  
            
    return render_template('createProfile.html')

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def showProfile(id):
    if request.method == "GET":
        user = User.query.filter_by(user_id = id).first()
        profile = Profile.query.filter_by(user_id=id).first()
        if not profile:
            return redirect(url_for('createProfile'))
        
        print(profile.avatar_url)
        
        edit = True
        requests = False
        friends = False
        if id != current_user.user_id:
            edit = False
            friends = Friends.query.filter(((Friends.user1_id == id) & (Friends.user2_id == current_user.user_id)) | ((Friends.user1_id == current_user.user_id) &(Friends.user2_id == id))).first()
            if friends:
                friends = True
            else:
                friends = False
            requests = Friend_Requests.query.filter(((Friend_Requests.receiver_id == id) & (Friend_Requests.sender_id == current_user.user_id)) | ((Friend_Requests.sender_id == id) & (Friend_Requests.receiver_id == current_user.user_id))).first()
            if requests:
                requests = True
            else:
                requests = False
        else:
            edit = True
        
        return render_template('showProfile.html', friends = friends, requests = requests, edit = edit, name = user.name, bio = profile.bio, status = profile.status, location = profile.location, interests = ", ".join(profile.interests), conditions = ", ".join(profile.conditions), users_avatar_url = user.avatar_url, avatar_url = current_user.avatar_url, private = profile.private, other_users_id = id, user_id = current_user.user_id)
    return render_template('showProfile.html')
    
# FRIENDS:
@app.route('/friends', methods = ['GET', 'POST'])
@login_required
def viewFriends():
    if request.method == 'GET':
        users = []
        friends = Friends.query.filter((Friends.user1_id == current_user.user_id) | (Friends.user2_id == current_user.user_id)).all()
        for friend in friends:
            if (friend.user1_id == current_user.user_id):
                users.append(User.query.filter_by(user_id = friend.user2_id).first())
                
            else:
                user = User.query.filter_by(user_id = friend.user1_id).first()
                users.append(user)
            
        requests = Friend_Requests.query.filter((Friend_Requests.receiver_id == current_user.user_id) | (Friend_Requests.sender_id == current_user.user_id)).all()
        requests_received = []
        requests_sent = []
        for req in requests:
            if(req.sender_id == current_user.user_id and req.status == 'pending'):
                receiver = User.query.filter_by(user_id = req.receiver_id).first()
                requests_sent.append({'user': receiver, 'req_id': req.request_id})
                
            elif (req.receiver_id == current_user.user_id and req.status == 'pending'):
                sender = User.query.filter_by(user_id = req.sender_id).first()
                requests_received.append({'user': sender, 'req_id': req.request_id})
                
        return render_template('friends.html', friends = users, requests_received = requests_received, requests_sent = requests_sent, avatar_url = current_user.avatar_url, user_id = current_user.user_id)
        
    return render_template('friends.html')


@app.route('/friends/requests/send/<int:input_request_id>', methods = ['POST'])
@login_required
def send_friend_request(input_request_id):
    
    sender = current_user.user_id
    receiver = input_request_id
    
    existingRequest = Friend_Requests.query.filter((Friend_Requests.sender_id == sender) & (Friend_Requests.receiver_id == receiver)).all()
    existingFriendship = Friends.query.filter(((Friends.user1_id == sender) & (Friends.user2_id == receiver)) | ((Friends.user2_id == sender) & (Friends.user1_id == receiver))).all()
    if(existingRequest or existingFriendship):
        print("not sent")
        return redirect(url_for('viewFriends'))
    
    friendRequest = Friend_Requests(sender_id = sender, receiver_id = receiver)
    db.session.add(friendRequest)
    db.session.commit()
    
    return redirect(url_for('viewFriends'))
    
@app.route('/friends/requests/<action>/<int:input_request_id>', methods = ['POST'])
@login_required    
def handle_friend_request(action, input_request_id):
    friend_request = Friend_Requests.query.filter_by(request_id = input_request_id).first()
    if not friend_request or friend_request.receiver_id != current_user.user_id:
        flash("Invalid friend request.", "danger")
        return redirect(url_for('viewFriends'))
    
    if action == 'accept':
        friend_request.status = 'accepted'
        if(friend_request.receiver_id < friend_request.sender_id):
            new_friendship = Friends(user1_id = friend_request.receiver_id, user2_id = friend_request.sender_id)
        elif(friend_request.sender_id < friend_request.receiver_id):
            new_friendship = Friends(user1_id = friend_request.sender_id, user2_id = friend_request.receiver_id)
        db.session.add(new_friendship)
    
    elif action == 'reject':
        friend_request.status = 'rejected'
        
    db.session.commit()
    return redirect(url_for('viewFriends'))
    
@app.route('/friends/search', methods = ['GET', 'POST'])
@login_required
def search_users():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    results = User.query.filter((User.username.ilike(f"%{query}%")) & (User.username != current_user.username)).limit(10).all()
    
    users_list = []
    for user in results:
        profile = Profile.query.filter(Profile.user_id == user.user_id).first()
        friends = Friends.query.filter(((Friends.user1_id == user.user_id) & (Friends.user2_id == current_user.user_id)) | ((Friends.user1_id == current_user.user_id) &(Friends.user2_id == user.user_id))).first()
        if friends:
            friends = True
        else:
            friends = False
        requests = Friend_Requests.query.filter(((Friend_Requests.receiver_id == user.user_id) & (Friend_Requests.sender_id == current_user.user_id)) | ((Friend_Requests.sender_id == user.user_id) & (Friend_Requests.receiver_id == current_user.user_id))).first()
        if requests:
            requests = True
        else:
            requests = False
        users_list.append({
            'id': user.user_id, 
            'username': user.username,
            'private': profile.private if profile else True,
            'friends': friends,
            'requests': requests
        }) 

    return jsonify(users_list)

# GROUPS:
@app.route('/groups', methods = ['GET', 'POST'])
@login_required
def viewGroups():
    if request.method == 'GET':
        groups = []
        group_ids = GroupMembers.query.filter(GroupMembers.user_id == current_user.user_id).all()
        for id in group_ids:
            group = Groups.query.filter(Groups.group_id == id.group_id).first()
            groups.append({'name': group.name, 'id': group.group_id, 'avatar': group.avatar_link})
        
        requests_received = []
        groups_created = Groups.query.filter(Groups.creator_id == current_user.user_id).all()
        group_created_id = [g.group_id for g in groups_created]
        requests_r = GroupRequests.query.filter(GroupRequests.group_id.in_(group_created_id)).all()
        for req in requests_r:
            if req.status == 'pending':
                group = next((g for g in groups_created if g.group_id == req.group_id), None)
                user = User.query.filter(User.user_id == req.user_id).first()
                if group:
                    requests_received.append({'group': group, 'requester': user, 'request_id': req.group_request_id})
           
        requests = GroupRequests.query.filter(GroupRequests.user_id == current_user.user_id).all()
        requests_sent = []
        for req in requests:
            if(req.status == 'pending'):
                group = Groups.query.filter_by(group_id = req.group_id).first()
                requests_sent.append({'group': group, 'req_id': req.group_request_id})
        return render_template('groups.html', groups = groups, requests_received = requests_received, requests_sent = requests_sent, avatar_url = current_user.avatar_url, user_id = current_user.user_id)
        
    return render_template('groups.html')

@app.route('/groups/create', methods = ['GET', 'POST'])
@login_required
def createGroup():
    print("before post check")
    if request.method == 'POST':
        print("in post")
        group_name = request.form['name']
        group_description = request.form['description']
        _creator = current_user.username
        _creator_id = current_user.user_id
        _avatar_link = request.files.get('avatar_file')
        url = upload_avatar_to_cloudinary(_avatar_link, current_user.user_id)
        
        new_group = Groups(name = group_name, creator_id = _creator_id, creator = _creator, description = group_description, avatar_link = url)
        
        db.session.add(new_group)
        new_id = Groups.query.filter(Groups.name == group_name).first().group_id
        new_member = GroupMembers(group_id = new_id, user_id = current_user.user_id)
        db.session.add(new_member)
        db.session.commit()
        print("group added successfully")
        group = Groups.query.filter(Groups.name == group_name).first()
        print(group.name)
        return redirect(url_for('viewGroups'))
        
    return redirect(url_for('viewGroups'))

@app.route('/groups/requests/send/<int:input_group_id>', methods = ['POST'])
@login_required
def send_group_request(input_group_id):
    
    user = current_user.user_id
    group = input_group_id
    
    existingRequest = GroupRequests.query.filter((GroupRequests.user_id == user) & (GroupRequests.group_id == group)).all()
    existingMember = GroupMembers.query.filter((GroupMembers.user_id == user) & (GroupMembers.group_id == group)).all()
    if(existingRequest or existingMember):
        print("not sent")
        return redirect(url_for('viewGroups'))
    
    groupRequest = GroupRequests(user_id = user, group_id = group)
    db.session.add(groupRequest)
    db.session.commit()
    
    print("successfully requested")
    
    return redirect(url_for('viewGroups'))

@app.route('/groups/requests/<action>/<int:input_request_id>', methods = ['POST'])
@login_required    
def handle_group_request(action, input_request_id):
    group_request = GroupRequests.query.filter(GroupRequests.group_request_id == input_request_id).first()
    group = Groups.query.filter(Groups.group_id == group_request.group_id).first()
    
    if not group_request or group.creator_id != current_user.user_id:
        flash("Invalid friend request.", "danger")
        return redirect(url_for('viewGroups'))
    
    if action == 'accept':
        group_request.status = 'accepted'
        new_group_member = GroupMembers(group_id = group.group_id, user_id = group_request.user_id)
        db.session.add(new_group_member)
    
    elif action == 'reject':
        group_request.status = 'rejected'
        
    db.session.commit()
    return redirect(url_for('viewGroups'))

@app.route('/groups/search', methods = ['GET', 'POST'])
@login_required
def search_groups():
    query = request.args.get('groupInput')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    results = Groups.query.filter(Groups.name.ilike(f"%{query}%")).limit(10).all()

    groups_list = []
    for group in results:
        created = False
        if(group.creator_id == current_user.user_id):
            created = True
        member = False
        join = GroupMembers.query.filter((GroupMembers.group_id == group.group_id) & (GroupMembers.user_id == current_user.user_id)).first()
        if(join):
            member = True
        requested = False
        existing_request = GroupRequests.query.filter((GroupRequests.group_id == group.group_id) & (GroupRequests.user_id == current_user.user_id)).first()
        if (existing_request):
            requested = True
        groups_list.append({
            'id': group.group_id, 
            'name': group.name,
            'created': created,
            'member': member,
            'request': requested
        }) 

    return jsonify(groups_list)

@app.route('/groups/profile/<int:id>', methods = ['GET', 'POST'])
@login_required
def group_profile(id):
    group_returned = Groups.query.filter(Groups.group_id == id).first()
    return render_template('groupProfile.html', user_id = current_user.user_id, avatar_url = current_user.avatar_url, name = group_returned.name, creator = group_returned.creator, description = group_returned.description, group_avatar = group_returned.avatar_link)

@app.route('/messages', methods = ['GET', 'POST'])
@login_required
def viewMessageBoard():
    friends1 = Friends.query.filter(Friends.user1_id == current_user.user_id).all()
    friends2 = Friends.query.filter(Friends.user2_id == current_user.user_id).all()
    friend_ids = [f.user2_id for f in friends1] + [f.user1_id for f in friends2]
    friend_message = []
    for id in friend_ids:
        friend = User.query.filter(User.user_id == id).first()
        last_message = Messages.query.filter(((Messages.sender_id == current_user.user_id) & (Messages.receiver_id == id))|((Messages.receiver_id == current_user.user_id) & (Messages.sender_id == id))).order_by(Messages.time_sent.desc()).first()
        if last_message:
            last_message.content = f.decrypt(last_message.content.encode()).decode()
            
        friend_message.append({'friend': friend, 'message': last_message})
    
    return render_template('messages.html', friend_message = friend_message, user_id = current_user.user_id, avatar_url = current_user.avatar_url)

@app.route('/messages/<int:receiver>', methods = ['GET', 'POST'])
@login_required
def viewMessages(receiver):
    messages = Messages.query.filter(((Messages.sender_id == current_user.user_id) & (Messages.receiver_id == receiver))|((Messages.receiver_id == current_user.user_id) & (Messages.sender_id == receiver))).order_by(Messages.time_sent.desc()).all()
    for message in messages:
        message.content = f.decrypt(message.content.encode()).decode()
        if message.sender_id == receiver:
            message.is_read = True
    
    return render_template('messageFeed.html', receive = receiver, messages = messages, user_id = current_user.user_id, avatar_url = current_user.avatar_url)
    
@app.route('/messages/send/<int:receiver>', methods = ['GET', 'POST'])
@login_required
def sendMessage(receiver):
    if request.method == 'POST':
        content = request.form['content']
        encrypted_content = f.encrypt(content.encode()).decode() 
        new_message = Messages(sender_id = current_user.user_id, receiver_id = receiver, content = encrypted_content)
        
        db.session.add(new_message)
        db.session.commit()
        
        return redirect(url_for('viewMessages', receiver = receiver))
    return redirect(url_for('viewMessages', receiver = receiver))
        

API_KEY = os.getenv('API_KEY')
AUTH_ENDPOINT = "https://utslogin.nlm.nih.gov/cas/v1/api-key"
SEARCH_ENDPOINT = "https://uts-ws.nlm.nih.gov/rest/search/current"
DEFINITIONS_ENDPOINT = "https://uts-ws.nlm.nih.gov/rest/content/current/CUI"
def get_tgt(api_key):
    params = {'apikey': api_key}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(AUTH_ENDPOINT, data=params, headers=headers)
    if response.status_code == 201:
        tgt_url = response.headers['location']
        return tgt_url
    return None

def get_service_ticket(tgt_url):
    params = {'service': 'http://umlsks.nlm.nih.gov'}
    response = requests.post(tgt_url, data=params)
    print("service ticket", response.text)
    return response.text if response.status_code == 200 else None

def get_definitions(cui, st, language= "ENG"):
    rootsource_map = {
        "ENG": ["MSH", "HPO", "NCI"] # Common English sources
    }
    url = f"https://uts-ws.nlm.nih.gov/rest/content/2023AA/CUI/{cui}/definitions"
    params = {"ticket": st}
    response = requests.get(url, params)
    print("Reponse text", response.text)
    print("Response url", response.url)
    if response.status_code == 200:
        defs = response.json()['result']
        allowed_sources = rootsource_map.get(language.upper(), [])
        filtered_defs = [d.get("value") for d in defs if d.get("rootSource") in allowed_sources and d.get("value")]
        print("Filtered defs")
        return filtered_defs or ["No definitions available in this version."]
    print("not 200")
    return ["Definition lookup failed."]

@app.route('/search', methods=['GET', 'POST'])
@login_required
def index():
    search_results = []
    error = None
    if request.method == 'POST':
        query = request.form['query']
        tgt = get_tgt(API_KEY)
        if tgt:
            st = get_service_ticket(tgt)
            if st:
                params = {
                    'string': query,
                    'ticket': st
                }
                response = requests.get(SEARCH_ENDPOINT, params=params)
                if response.status_code == 200:
                    search_items = response.json()['result']['results']
                    for item in search_items[:5]:  # limit to top 5 for speed
                        cui = item.get('ui')
                        name = item.get('name')
                        print("CUI", cui)
                        if cui and cui != 'NONE':
                            tgt = get_tgt(API_KEY)
                            st = get_service_ticket(tgt)
                            definitions = get_definitions(cui, st)
                            search_results.append({
                                'name': name,
                                'cui': cui,
                                'definitions': definitions
                            })
                else:
                    error = "Failed to fetch search results."
            else:
                error = "Failed to get service ticket."
        else:
            error = "Failed to get authentication ticket."

    return render_template('index.html', results=search_results, error=error)

# LOGOUT:
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)