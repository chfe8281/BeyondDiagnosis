async function searchUsers(query) {
  const res = await fetch(`/api/users/search?query=${encodeURIComponent(query)}`);
  const users = await res.json();
  console.log(users);
}

async function sendFriendRequest(userId) {
  try {
    const response = await fetch(`/friends/requests/send/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
      window.location.href = '/friends';
    } else {
      alert("Failed to send request");
    }
  } catch (err) {
    console.error(err);
    alert("Error occurred");
  }
}

async function sendGroupRequest(groupId) {
  try {
    const response = await fetch(`/groups/requests/send/${groupId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
      window.location.href = '/groups';
    } else {
      alert("Failed to send request");
    }
  } catch (err) {
    console.error(err);
    alert("Error occurred");
  }
}

document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById("user-search");
  const resultsDiv = document.getElementById("search_results");

  if(searchInput) {
    searchInput.addEventListener("input", async () => {
      const query = searchInput.value.trim();
      if (query.length === 0) {
        resultsDiv.innerHTML = "";
        resultsDiv.style.display = "none";
        return;
      }

      const response = await fetch(`friends/search?query=${encodeURIComponent(query)}`);
      const users = await response.json();
      console.log(users)

      if (users.length === 0) {
        resultsDiv.innerHTML = "<div class='dropdown-item'>No users found</div>";
      } else {
      
          resultsDiv.innerHTML = users.map(user => {
              const usernameHTML = user.private
                  ? `${user.username}`
                  : `<a href="/profile/${user.id}" class="profile-link" onclick="event.stopPropagation()">${user.username}</a>`;
              const buttonHTML = user.friends
                  ? `<button class="friendReq_Button" type="button" disabled>Friends</button>`
                  : user.requests
                      ? `<button class="friendReq_Button" type="button" disabled>Request Sent</button>`
                      : `<button class="friendReq_Button" type="button" onclick="event.stopPropagation(); sendFriendRequest(${user.id})">
                          Add Friend
                          </button>`;

                  return `
              <div class="dropdown-item">
                  ${usernameHTML}
                  ${buttonHTML}
              </div>`}).join('');
      }

      resultsDiv.style.display = "block";
    });
  }

  const modal = document.getElementById('groupModal');
  const openBtn = document.getElementById('groupModalBtn');
  const closeBtn = document.getElementById('closeGroupModalBtn');
  const form = document.getElementById('groupForm');

  if(modal){
    openBtn.onclick = () => {
      modal.style.display = 'block';
    };

    closeBtn.onclick = () => {
      modal.style.display = 'none';
    };

    window.onclick = event => {
      if (event.target == modal) {
        modal.style.display = 'none';
      }
    };
  }

  const groupInput = document.getElementById("groupInput");
  const groupResultsDiv = document.getElementById("group_results");

  if(groupInput)
  {
    groupInput.addEventListener("input", async () => {
      const query = groupInput.value.trim();
      if (query.length === 0) {
        groupResultsDiv.innerHTML = "";
        groupResultsDiv.style.display = "none";
        return;
      }

      const group_response = await fetch(`/groups/search?groupInput=${encodeURIComponent(query)}`);
      const groups = await group_response.json();
      console.log(groups)

      if (groups.length === 0) {
        groupResultsDiv.innerHTML = "<div class='dropdown-item'>No groups found</div>";
      } 
      else {
        groupResultsDiv.innerHTML = groups.map(group => {
          const button = group.created
                  ? `<button class="friendReq_Button" type="button" disabled>Created</button>`
                  : group.member
                      ? `<button class="friendReq_Button" type="button" disabled>Member</button>`
                      : group.request
                        ? `<button class="friendReq_Button" type="button" disabled>Requested</button>`
                        : `<button class="friendReq_Button" type="button" onclick="event.stopPropagation(); sendGroupRequest(${group.id})">Request to Join</button>`;

        return `
              <div class="dropdown-item" onclick="selectGroup('${group.name}')">
                  <a href="/groups/profile/${group.id}" class="profile-link">${group.name}</a>
                  ${button}
              </div>`}).join('');
      }

      groupResultsDiv.style.display = "block";
    });
  }
});

function selectGroup(name) {
  document.getElementById("groupInput").value = name;
  document.getElementById("group_results").style.display = "none";
}

function selectUser(name) {
  document.getElementById("user-search").value = name;
  document.getElementById("search_results").style.display = "none";
}
