document.addEventListener('DOMContentLoaded', function() {
    fetch('/teams')
        .then(response => response.json())
        .then(data => {
            const teamsList = document.getElementById('teams-list');
            if (data.teams && data.teams.length > 0) {
                const ul = document.createElement('ul');
                data.teams.forEach(team => {
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = `/team.html?team=${encodeURIComponent(team)}`;
                    a.textContent = team;
                    a.style.textDecoration = 'none';
                    a.style.color = 'inherit';
                    li.appendChild(a);
                    ul.appendChild(li);
                });
                teamsList.appendChild(ul);
            } else {
                teamsList.textContent = 'No teams found.';
            }
        })
        .catch(error => {
            console.error('Error fetching teams:', error);
            document.getElementById('teams-list').textContent = 'Error loading teams.';
        });
});