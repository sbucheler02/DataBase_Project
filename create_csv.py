import csv

# Based on the HTML sample provided, extracting the first goaltender:
# Carter Clafton (G)
# #35, Age 23, Born 2002 (03/12/2002), Birthplace: Grand Rapids, MN, USA
# Height: 6'2", Weight: 174, Shoots: L

players_data = [
    {
        'first_name': 'Carter',
        'last_name': 'Clafton',
        'team': 'Air Force Academy',
        'number': '35',
        'position': 'GOALTENDERS',
        'age': '23',
        'born': '2002',
        'birth_place': 'Grand Rapids, MN, USA',
        'height': "6'2\"",
        'weight': '174',
        'shoots': 'L'
    }
]

# Write to CSV
csv_file = '/workspaces/DataBase_Project/players.csv'
headers = ['first_name', 'last_name', 'team', 'number', 'position', 'age', 'born', 'birth_place', 'height', 'weight', 'shoots']

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(players_data)

print(f"CSV file created with {len(players_data)} player(s)")
print(f"First player: {players_data[0]['first_name']} {players_data[0]['last_name']}")
print(f"Position: {players_data[0]['position']}")
print(f"Team: {players_data[0]['team']}")
