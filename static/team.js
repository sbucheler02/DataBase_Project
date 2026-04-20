document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const team = urlParams.get('team');
    
    if (team) {
        document.getElementById('team-title').textContent = `${team} Players`;
        
        fetch(`/team/${encodeURIComponent(team)}/players`)
            .then(response => response.json())
            .then(data => {
                const playersList = document.getElementById('players-list');
                if (data.players_by_position && Object.keys(data.players_by_position).length > 0) {
                    for (const [position, players] of Object.entries(data.players_by_position)) {
                        const positionDiv = document.createElement('div');
                        positionDiv.className = 'position-section';
                        
                        const positionTitle = document.createElement('h2');
                        positionTitle.textContent = position;
                        positionDiv.appendChild(positionTitle);
                        
                        const ul = document.createElement('ul');
                        players.forEach(player => {
                            const li = document.createElement('li');
                            li.textContent = player;
                            li.className = 'player-item';
                            li.addEventListener('click', () => showPlayerModal(player, team));
                            ul.appendChild(li);
                        });
                        positionDiv.appendChild(ul);
                        playersList.appendChild(positionDiv);
                    }
                } else {
                    playersList.textContent = 'No players found for this team.';
                }
            })
            .catch(error => {
                console.error('Error fetching players:', error);
                document.getElementById('players-list').textContent = 'Error loading players.';
            });
    } else {
        document.getElementById('players-list').textContent = 'No team specified.';
    }
    
    document.getElementById('back-button').addEventListener('click', function() {
        window.location.href = '/';
    });
    
    // Modal functionality
    const modal = document.getElementById('player-modal');
    const closeBtn = document.getElementsByClassName('close')[0];
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

function showPlayerModal(playerName, team) {
    const [firstName, ...lastNameParts] = playerName.split(' ');
    const lastName = lastNameParts.join(' ');
    
    fetch(`/player/${encodeURIComponent(firstName)}/${encodeURIComponent(lastName)}?team=${encodeURIComponent(team)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Player not found');
                return;
            }
            
            const modal = document.getElementById('player-modal');
            const detailsDiv = document.getElementById('player-details');
            
            let html = `<h2>${data.bio.first_name} ${data.bio.last_name}</h2>`;
            
            // Bio section
            html += '<h3>Bio</h3><div class="bio-section">';
            for (const [key, value] of Object.entries(data.bio)) {
                if (value !== null && value !== undefined) {
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    html += `<p><strong>${label}:</strong> ${value}</p>`;
                }
            }
            html += '</div>';
            
            // Stats section
            if (data.stats) {
                html += '<h3>Stats</h3><div class="stats-section">';
                for (const [key, value] of Object.entries(data.stats)) {
                    if (value !== null && value !== undefined) {
                        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        html += `<p><strong>${label}:</strong> ${value}</p>`;
                    }
                }
                html += '</div>';
            } else {
                html += '<h3>Stats</h3><p>No stats available</p>';
            }
            
            detailsDiv.innerHTML = html;
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching player details:', error);
            alert('Error loading player details');
        });
}