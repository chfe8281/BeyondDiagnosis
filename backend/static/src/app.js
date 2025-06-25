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
      alert("Friend request sent!");
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
      resultsDiv.innerHTML = users.map(user => `
        <div class="dropdown-item" onclick="selectUser('${user.username}')">
            ${user.username}
            <button class="friendReq_Button" type="button" onclick="event.stopPropagation(); sendFriendRequest(${user.id})">Add Friend</button>
        </div>
      `).join('');
    }

    resultsDiv.style.display = "block";
  });
});

function selectUser(username) {
  document.getElementById("user-search").value = username;
  document.getElementById("search-results").style.display = "none";
}