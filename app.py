from flask import Flask, render_template, request
import csv
import datetime
import re

app = Flask(__name__)

# Dictionnaires globaux
months = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

months_fr = {
    1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril',
    5: 'mai', 6: 'juin', 7: 'juillet', 8: 'août',
    9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
}

days_fr = {
    '1': 'lundi', '2': 'mardi', '3': 'mercredi',
    '4': 'jeudi', '5': 'vendredi', '6': 'samedi', '7': 'dimanche'
}

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

def find_departure_year(dep_month, dep_day, target_isoweekday):
    current_year = datetime.datetime.now().year
    for year in range(current_year - 1, current_year + 2):
        try:
            candidate = datetime.datetime(year, dep_month, dep_day)
            if candidate.isoweekday() == target_isoweekday:
                return year
        except ValueError:
            continue
    return current_year

def parse_flight_info(flight_info):
    try:
        cleaned_info = flight_info.replace('*', ' ')
        parts = cleaned_info.split()
        if not parts:
            raise ValueError(f"Format invalide : {flight_info}")

        # Nouvelle regex pour accepter les codes alphanumériques
        first_part = parts[0]
        match = re.match(r"^([A-Za-z0-9]{2})(\d+)$", first_part)
        if match:
            airline_code = match.group(1).upper()
            flight_number = match.group(2)
            rest = parts[1:]
            required_rest = 5
            if len(rest) < required_rest:
                raise ValueError(f"Format invalide après code et numéro : {flight_info}")
            date_str = rest[0]
            day_code = rest[1]
            airports_pair = rest[2]
            departure_time = rest[3]
            arrival_time = rest[4]
            arrival_date_str = rest[5] if len(rest) > required_rest else date_str
        else:
            if len(parts) < 7:
                raise ValueError(f"Format invalide : {flight_info}")
            airline_code = parts[0]
            flight_number = parts[1]
            date_str = parts[2]
            day_code = parts[3]
            airports_pair = parts[4]
            departure_time = parts[5]
            arrival_time = parts[6]
            arrival_date_str = parts[7] if len(parts) > 7 else date_str

        departure_airport_code = airports_pair[:3]
        arrival_airport_code = airports_pair[3:]

        # Utilisation du dictionnaire days_fr global
        departure_day = days_fr.get(day_code, '')

        dep_day = int(date_str[:2])
        dep_month_str = date_str[2:5].upper()
        dep_month = months[dep_month_str]
        target_isoweekday = int(day_code)
        dep_year = find_departure_year(dep_month, dep_day, target_isoweekday)
        dep_date = datetime.datetime(dep_year, dep_month, dep_day)

        arrival_day = int(arrival_date_str[:2])
        arrival_month_str = arrival_date_str[2:5].upper()
        arrival_month = months[arrival_month_str]
        arrival_year = dep_year

        try:
            arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
        except ValueError:
            arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)

        if arr_date < dep_date:
            arrival_year += 1
            try:
                arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
            except ValueError:
                pass

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
    except Exception as e:
        raise ValueError(f"Erreur dans la ligne: '{flight_info}'\nDétail: {str(e)}")

def parse_flight_info_v2(flight_info):
    try:
        cleaned_info = flight_info.replace('*', ' ')
        parts = [p for p in cleaned_info.split() if p]
        
        if parts and parts[0].isdigit():
            parts = parts[1:]

        # Regex mise à jour pour accepter les codes alphanumériques
        if parts:
            match = re.match(r"^([A-Za-z0-9]{2})(\d+)$", parts[0])
            if match:
                airline_code = match.group(1)
                flight_number = match.group(2)
                parts = [airline_code, flight_number] + parts[1:]

        try:
            airline_code = parts[0]
            flight_number = parts[1]
            # Ajustement des indices
            date_str = parts[2]
            day_code = parts[3]
            airports_pair = parts[4]
            departure_time = parts[6]
            arrival_time = parts[7]
            arrival_date_str = parts[8] if len(parts) > 8 else date_str
        except IndexError as e:
            raise ValueError(f"Erreur de structure dans la ligne : {flight_info}\nDétail : {e}")

        if len(airports_pair) != 6 or not airports_pair.isalpha():
            raise ValueError(f"Format aéroports invalide : {airports_pair} dans la ligne : {flight_info}")

        dep_day = int(date_str[:2])
        dep_month_str = date_str[2:5].upper()
        dep_month = months.get(dep_month_str)
        
        if not dep_month:
            raise ValueError(f"Mois invalide : {dep_month_str}")

        target_isoweekday = int(day_code)
        dep_year = find_departure_year(dep_month, dep_day, target_isoweekday)
        
        try:
            dep_date = datetime.datetime(dep_year, dep_month, dep_day)
        except ValueError as e:
            raise ValueError(f"Date invalide: {e}")

        # Traitement de la date d'arrivée
        arrival_day = int(arrival_date_str[:2])
        arrival_month_str = arrival_date_str[2:5].upper()
        arrival_month = months.get(arrival_month_str)
        if not arrival_month:
            raise ValueError(f"Mois d'arrivée invalide : {arrival_month_str}")

        arrival_year = dep_year
        try:
            candidate_arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
        except ValueError as e:
            raise ValueError(f"Date d'arrivée invalide : {e}")

        if candidate_arr_date < dep_date:
            arrival_year += 1
            try:
                candidate_arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
            except ValueError as e:
                raise ValueError(f"Date d'arrivée invalide après ajustement : {e}")

        arr_date = candidate_arr_date

        return {
            'airline_code': airline_code,
            'flight_number': flight_number,
            'formatted_departure_date': f"{days_fr[day_code]} {dep_day} {months_fr[dep_month]}",
            'formatted_arrival_date': f"{days_fr[str(arr_date.isoweekday())]} {arr_date.day} {months_fr[arr_date.month]}",
            'departure_time': f"{departure_time[:2]}h{departure_time[2:]}",
            'arrival_time': f"{arrival_time[:2]}h{arrival_time[2:]}",
            'departure_airport': airports.get(airports_pair[:3], airports_pair[:3]),
            'departure_airport_code': airports_pair[:3],
            'arrival_airport': airports.get(airports_pair[3:], airports_pair[3:]),
            'arrival_airport_code': airports_pair[3:]
        }
    except Exception as e:
        raise ValueError(f"Erreur dans la ligne: '{flight_info}'\nDétail: {str(e)}")

def group_flights(flights):
    if not flights:
        return []
    return [(flights[0]['formatted_departure_date'], flights)]

def process_flight_data(flight_data, parser):
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

    aller_flights = groups[0] if groups else []
    retour_flights = []
    if len(groups) > 1:
        retour_flights = [flight for group in groups[1:] for flight in group]

    parsed_aller = []
    for flight in aller_flights:
        try:
            parsed = parser(flight)
            parsed_aller.append(parsed)
        except Exception as e:
            raise ValueError(f"Erreur dans le vol aller: {flight}\n{str(e)}")
    
    parsed_retour = []
    for flight in retour_flights:
        try:
            parsed = parser(flight)
            parsed_retour.append(parsed)
        except Exception as e:
            raise ValueError(f"Erreur dans le vol retour: {flight}\n{str(e)}")

    seen = set()
    airline_codes_order = []
    for flight in parsed_aller + parsed_retour:
        code = flight['airline_code']
        if code not in seen:
            seen.add(code)
            airline_codes_order.append(code)

    formatted_airlines = [f"{airlines.get(code, code)} ({code})" for code in airline_codes_order]
    
    return {
        'grouped_aller': group_flights(parsed_aller),
        'grouped_retour': group_flights(parsed_retour),
        'airlines_str': " et ".join(formatted_airlines) if len(formatted_airlines) == 1 else ", ".join(formatted_airlines[:-1]) + " et " + formatted_airlines[-1]
    }

def filter_amadeus_data(flight_data):
    filtered = []
    for line in flight_data.split('\n'):
        original_line = line.rstrip().replace('*', ' ')
        if not original_line.strip():
            filtered.append('')
            continue
        
        parts = original_line.split()
        try:
            # Nouvelle approche : trouver l'index de la date (format JJMMM)
            date_index = None
            for i, part in enumerate(parts):
                if re.match(r"\d{2}[A-Z]{3}", part):
                    date_index = i
                    break
            if date_index is None:
                raise ValueError("Aucune date trouvée")
            
            # Décalage pour ignorer le numéro de ligne s'il existe
            start_idx = 1 if parts[0].isdigit() else 0
            
            # Extraire le code airline et numéro de vol
            airline_flight = ''.join(parts[start_idx:date_index-1])
            match = re.match(r"^([A-Za-z0-9]{2})(\d+)$", airline_flight)
            if not match:
                # Tentative alternative pour les formats différents
                if date_index - start_idx >= 2:
                    airline_code = parts[start_idx]
                    flight_number = parts[start_idx+1]
                else:
                    raise ValueError("Format de code de vol invalide")
            else:
                airline_code = match.group(1)
                flight_number = match.group(2)
            
            # Extraire les composants clés
            date_str = parts[date_index]
            day_code = parts[date_index+1]
            airports_pair = parts[date_index+2]
            departure_time = parts[date_index+4]
            arrival_time = parts[date_index+5]
            arrival_date = parts[date_index+6] if len(parts) > date_index+6 else date_str
            
            # Construire la nouvelle ligne formatée
            new_line = f"{airline_code}{flight_number} {date_str} {day_code} {airports_pair} {departure_time} {arrival_time} {arrival_date}"
            filtered.append(new_line)
            
        except (ValueError, IndexError) as e:
            filtered.append(original_line + f" # Erreur: {str(e)}")
    
    return '\n'.join(filtered)

@app.route('/', methods=['GET', 'POST'])
def index():
    flight_data1 = request.form.get('flight_data1', '')
    flight_data2 = request.form.get('flight_data2', '')
    notes_itineraire = request.form.get('notes-itineraire', '')
    notes_siege = request.form.get('notes-siege', '')
    vols_value = request.form.get('vols', 'non-vols')
    hebergement_value = request.form.get('hebergement', 'non-hebergement')
    
    result1 = None
    result2 = None
    error_message = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Filtrer':
            try:
                flight_data1 = filter_amadeus_data(flight_data2)
            except Exception as e:
                error_message = f"Erreur lors du filtrage : {str(e)}"
            
        elif action == 'Convertir':
            if 'flight_data1' in request.form:
                try:
                    result1 = process_flight_data(flight_data1, parse_flight_info)
                except Exception as e:
                    error_message = f"Erreur lors de la conversion (Format filtré) : {str(e)}"
            elif 'flight_data2' in request.form:
                try:
                    result2 = process_flight_data(flight_data2, parse_flight_info_v2)
                except Exception as e:
                    error_message = f"Erreur lors de la conversion (Format original) : {str(e)}"

    return render_template('index.html',
                        result1=result1,
                        result2=result2,
                        flight_data1=flight_data1,
                        flight_data2=flight_data2,
                        notes_itineraire=notes_itineraire,
                        notes_siege=notes_siege,
                        vols=vols_value,
                        hebergement=hebergement_value,
                        error_message=error_message)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)