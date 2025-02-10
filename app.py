from flask import Flask, render_template, request
import csv
import datetime

app = Flask(__name__)

def load_mapping(filename):
    mapping = {}
    try:
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if row:
                    mapping[row[0]] = row[1]
    except FileNotFoundError:
        print(f"Attention: Fichier {filename} non trouvé")
    return mapping

airlines = load_mapping('airlines.csv')
airports = load_mapping('airports.csv')

def parse_flight_info(flight_info):
    parts = flight_info.split()
    if len(parts) < 7:
        raise ValueError(f"Format invalide : {flight_info}")

    # Extraction des éléments de base
    airline_code = parts[0]
    flight_number = parts[1]
    date_str = parts[2]
    day_code = parts[3]
    airports_pair = parts[4]
    departure_time = parts[5]
    arrival_time = parts[6]
    arrival_date_str = parts[7] if len(parts) > 7 else date_str

    # Découpage des aéroports
    departure_airport_code = airports_pair[:3]
    arrival_airport_code = airports_pair[3:]

    # Traduction des jours
    days_fr = {
        '1': 'Lundi', '2': 'Mardi', '3': 'Mercredi',
        '4': 'Jeudi', '5': 'Vendredi', '6': 'Samedi', '7': 'Dimanche'
    }
    departure_day = days_fr.get(day_code, '')

    # Conversion des dates
    months = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    
    def parse_date(date_str):
        day = int(date_str[:2])
        month_str = date_str[2:5].upper()
        return datetime.datetime(2023, months[month_str], day)  # Année arbitraire

    dep_date = parse_date(date_str)
    arr_date = parse_date(arrival_date_str)
    
    # Formatage français
    months_fr = {
        1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril',
        5: 'mai', 6: 'juin', 7: 'juillet', 8: 'août',
        9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
    }

    formatted_departure = f"{departure_day} {dep_date.day} {months_fr[dep_date.month]}"
    formatted_arrival = f"{days_fr[str(arr_date.isoweekday())]} {arr_date.day} {months_fr[arr_date.month]}"

    return {
        'airline_code': airline_code,
        'airline': airlines.get(airline_code, airline_code),
        'flight_number': flight_number,
        'formatted_departure_date': formatted_departure,
        'formatted_arrival_date': formatted_arrival,
        'departure_time': f"{departure_time[:2]}h{departure_time[2:]}",
        'arrival_time': f"{arrival_time[:2]}h{arrival_time[2:]}",
        'departure_airport': airports.get(departure_airport_code, departure_airport_code),
        'departure_airport_code': departure_airport_code,
        'arrival_airport': airports.get(arrival_airport_code, arrival_airport_code),
        'arrival_airport_code': arrival_airport_code
    }

def group_flights(flights):
    grouped = []
    if not flights:
        return grouped
    
    current_date = flights[0]['formatted_departure_date']
    current_group = []

    for flight in flights:
        if flight['formatted_departure_date'] == current_date:
            current_group.append(flight)
        else:
            grouped.append((current_date, current_group))
            current_date = flight['formatted_departure_date']
            current_group = [flight]
    
    if current_group:
        grouped.append((current_date, current_group))
    
    return grouped

@app.route('/', methods=['GET', 'POST'])
def index():
    flight_data_value = ""
    
    if request.method == 'POST':
        flight_data = request.form['flight_data']
        flight_data_value = flight_data

        # Découpage en groupes
        groups = []
        current_group = []
        for line in flight_data.split('\n'):
            stripped = line.strip()
            if not stripped:
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(stripped)
        if current_group:
            groups.append(current_group)

        # Traitement des vols
        aller_flights = groups[0] if groups else []
        retour_flights = []
        if len(groups) > 1:
            retour_flights = [flight for group in groups[1:] for flight in group]

        # Parsing
        parsed_aller = [parse_flight_info(flight) for flight in aller_flights]
        parsed_retour = [parse_flight_info(flight) for flight in retour_flights]

        # Collecte des compagnies aériennes
        airline_codes = set()
        for flight in aller_flights + retour_flights:
            if flight.split():
                airline_codes.add(flight.split()[0])

        formatted_airlines = [
            f"{airlines.get(code, code)} ({code})" 
            for code in sorted(airline_codes)
        ]

        # Groupement par date
        grouped_aller = group_flights(parsed_aller)
        grouped_retour = group_flights(parsed_retour)

        return render_template('index.html',
                            grouped_aller=grouped_aller,
                            grouped_retour=grouped_retour,
                            formatted_airlines=formatted_airlines,
                            flight_data=flight_data_value)
    
    return render_template('index.html', flight_data=flight_data_value)

if __name__ == '__main__':
    app.run(debug=True)