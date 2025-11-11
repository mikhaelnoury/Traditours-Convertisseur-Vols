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

def format_day(day):
    """Formate le jour avec '1er' pour le premier du mois"""
    if day == 1:
        return "1<sup>er</sup>"
    return str(day)

def format_airport_name(airport_code, airport_name):
    """Retire 'Aéroport de ' pour les codes XDS et BQC"""
    if airport_code in ['XDS', 'BQC']:
        return airport_name.replace("Aéroport de ", "")
    return airport_name

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

        formatted_departure = f"{days_fr[day_code]} {format_day(dep_day)} {months_fr[dep_month]}"
        formatted_arrival = f"{days_fr[str(arr_date.isoweekday())]} {format_day(arr_date.day)} {months_fr[arr_date.month]}"

        # Formatage spécial des noms d'aéroport
        departure_airport_name = airports.get(departure_airport_code, departure_airport_code)
        arrival_airport_name = airports.get(arrival_airport_code, arrival_airport_code)
        
        departure_airport_name = format_airport_name(departure_airport_code, departure_airport_name)
        arrival_airport_name = format_airport_name(arrival_airport_code, arrival_airport_name)

        # Calculer si le départ et l'arrivée sont le même jour
        same_day = (dep_date.date() == arr_date.date())

        return {
            'airline_code': airline_code,
            'airline': airlines.get(airline_code, airline_code),
            'flight_number': flight_number,
            'formatted_departure_date': formatted_departure,
            'formatted_arrival_date': formatted_arrival,
            'departure_time': f"{departure_time[:2]}h{departure_time[2:]}",
            'arrival_time': f"{arrival_time[:2]}h{arrival_time[2:]}",
            'departure_airport': departure_airport_name,
            'departure_airport_code': departure_airport_code,
            'arrival_airport': arrival_airport_name,
            'arrival_airport_code': arrival_airport_code,
            'same_day': same_day  # Nouveau champ
        }
    except Exception as e:
        raise ValueError(f"Erreur dans la ligne: '{flight_info}'\nDétail: {str(e)}")

def parse_flight_info_v2(flight_info):
    try:
        cleaned_info = flight_info.replace('*', ' ').replace('# Erreur:', '').strip()
        parts = [p for p in cleaned_info.split() if p]
        
        if not parts:
            raise ValueError("Ligne vide")
        
        # Supprimer le numéro de ligne si présent
        if parts[0].isdigit():
            parts = parts[1:]
            if not parts:
                raise ValueError("Rien après le numéro de ligne")

        # Gestion du code airline et numéro de vol
        airline_code = parts[0]
        flight_number = parts[1]
        
        # Vérifier si le code airline et le numéro sont fusionnés
        if len(parts) > 1 and re.match(r"^[A-Za-z0-9]{2}\d+$", airline_code):
            match = re.match(r"^([A-Za-z0-9]{2})(\d+)$", airline_code)
            if match:
                airline_code = match.group(1)
                flight_number = match.group(2)
                # Reconstruire les parties
                parts = [airline_code, flight_number] + parts[1:]

        # Trouver les indices de toutes les dates
        date_indices = []
        for i, part in enumerate(parts):
            if re.match(r"\d{2}[A-Z]{3}", part):
                date_indices.append(i)
        
        if not date_indices:
            raise ValueError("Aucune date trouvée dans la ligne")
        
        # La première date est la date de départ
        date_index = date_indices[0]
        
        # Extraction des composants
        date_str = parts[date_index]
        day_code = parts[date_index + 1]
        airports_pair = parts[date_index + 2]
        
        # Si nous avons une deuxième date, c'est la date d'arrivée
        if len(date_indices) > 1:
            # La date d'arrivée est après les heures
            departure_time = parts[date_index + 3]
            arrival_time = parts[date_index + 4]
            arrival_date_str = parts[date_indices[1]]
        else:
            # Sinon, nous utilisons la structure par défaut
            departure_time = parts[date_index + 3]
            arrival_time = parts[date_index + 4]
            arrival_date_str = parts[date_index + 5] if len(parts) > date_index + 5 else date_str

        # Validation des aéroports
        if len(airports_pair) != 6 or not airports_pair.isalpha():
            raise ValueError(f"Format aéroports invalide: {airports_pair}")

        # Traitement des dates
        dep_day = int(date_str[:2])
        dep_month_str = date_str[2:5].upper()
        dep_month = months.get(dep_month_str)
        
        if not dep_month:
            raise ValueError(f"Mois invalide: {dep_month_str}")

        target_isoweekday = int(day_code)
        dep_year = find_departure_year(dep_month, dep_day, target_isoweekday)
        
        try:
            dep_date = datetime.datetime(dep_year, dep_month, dep_day)
        except ValueError as e:
            raise ValueError(f"Date de départ invalide: {e}")

        # Traitement de la date d'arrivée
        arrival_day = int(arrival_date_str[:2])
        arrival_month_str = arrival_date_str[2:5].upper()
        arrival_month = months.get(arrival_month_str)
        
        if not arrival_month:
            raise ValueError(f"Mois d'arrivée invalide: {arrival_month_str}")

        arrival_year = dep_year
        try:
            arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
        except ValueError:
            # Ajustement si la date d'arrivée est invalide
            arrival_year += 1
            try:
                arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
            except ValueError as e:
                raise ValueError(f"Date d'arrivée invalide: {e}")

        # Vérifier si la date d'arrivée est avant la date de départ
        if arr_date < dep_date:
            arrival_year += 1
            try:
                arr_date = datetime.datetime(arrival_year, arrival_month, arrival_day)
            except ValueError as e:
                raise ValueError(f"Date d'arrivée invalide après ajustement: {e}")

        # Formatage des noms d'aéroport
        departure_airport_code = airports_pair[:3]
        arrival_airport_code = airports_pair[3:]
        
        departure_airport_name = airports.get(departure_airport_code, departure_airport_code)
        arrival_airport_name = airports.get(arrival_airport_code, arrival_airport_code)
        
        departure_airport_name = format_airport_name(departure_airport_code, departure_airport_name)
        arrival_airport_name = format_airport_name(arrival_airport_code, arrival_airport_name)

        # Calculer si le départ et l'arrivée sont le même jour
        same_day = (dep_date.date() == arr_date.date())

        return {
            'airline_code': airline_code,
            'airline': airlines.get(airline_code, airline_code),
            'flight_number': flight_number,
            'formatted_departure_date': f"{days_fr[day_code]} {format_day(dep_day)} {months_fr[dep_month]}",
            'formatted_arrival_date': f"{days_fr[str(arr_date.isoweekday())]} {format_day(arr_date.day)} {months_fr[arr_date.month]}",
            'departure_time': f"{departure_time[:2]}h{departure_time[2:]}",
            'arrival_time': f"{arrival_time[:2]}h{arrival_time[2:]}",
            'departure_airport': departure_airport_name,
            'departure_airport_code': departure_airport_code,
            'arrival_airport': arrival_airport_name,
            'arrival_airport_code': arrival_airport_code,
            'same_day': same_day
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
    # Nettoyer d'abord le texte pour ne garder que les lignes de vol
    cleaned_data = clean_flight_text(flight_data)
    
    filtered = []
    for line in cleaned_data.split('\n'):
        original_line = line.rstrip()
        if not original_line.strip():
            filtered.append('')
            continue
        
        try:
            # Nettoyer la ligne
            cleaned_line = original_line.replace('*', ' ')
            parts = cleaned_line.split()
            
            # Ignorer le numéro de ligne
            if parts and parts[0].isdigit():
                parts = parts[1:]
            
            if not parts:
                continue
            
            # Trouver toutes les dates
            dates = [part for part in parts if re.match(r"\d{2}[A-Z]{3}", part)]
            if len(dates) < 1:
                raise ValueError("Aucune date trouvée")
            
            # La première date est le départ
            dep_date_str = dates[0]
            
            # Trouver l'index de la date de départ
            dep_date_index = None
            for i, part in enumerate(parts):
                if part == dep_date_str:
                    dep_date_index = i
                    break
            
            if dep_date_index is None:
                raise ValueError("Date de départ non trouvée")
            
            # Composants fixes après la date de départ
            day_code = parts[dep_date_index + 1]
            airports_pair = parts[dep_date_index + 2]
            
            # Code airline et numéro de vol
            airline_code = parts[0]
            flight_number = parts[1]
            
            # S'assurer que le code airline et le numéro de vol sont séparés
            if re.match(r"^[A-Za-z0-9]{2}\d+$", airline_code):
                match = re.match(r"^([A-Za-z0-9]{2})(\d+)$", airline_code)
                if match:
                    airline_code = match.group(1)
                    flight_number = match.group(2)
            
            # Trouver les heures (recherche des motifs 4 chiffres)
            times = []
            time_offset = 0
            for part in parts:
                if re.match(r"^\d{4}(\+\d+)?$", part):
                    time_match = re.match(r"^(\d{4})(?:\+(\d+))?$", part)
                    if time_match:
                        times.append(time_match.group(1))
                        if time_match.group(2):
                            time_offset = int(time_match.group(2))
            
            if len(times) < 2:
                raise ValueError("Heures insuffisantes")
            
            departure_time, arrival_time = times[0], times[1]
            
            # Déterminer la date d'arrivée
            if len(dates) > 1:
                # Utiliser la deuxième date comme date d'arrivée
                arr_date_str = dates[1]
            else:
                # Calculer avec l'offset
                dep_day = int(dep_date_str[:2])
                dep_month_str = dep_date_str[2:5].upper()
                dep_month = months.get(dep_month_str)
                
                if not dep_month:
                    raise ValueError(f"Mois invalide: {dep_month_str}")
                
                target_isoweekday = int(day_code)
                dep_year = find_departure_year(dep_month, dep_day, target_isoweekday)
                
                dep_date = datetime.datetime(dep_year, dep_month, dep_day)
                arr_date = dep_date + datetime.timedelta(days=time_offset)
                arr_date_str = f"{arr_date.day:02d}{dep_date_str[2:5].upper()}"
            
            # Construire la ligne filtrée
            new_line = f"{airline_code} {flight_number} {dep_date_str} {day_code} {airports_pair} {departure_time} {arrival_time} {arr_date_str}"
            filtered.append(new_line)
            
        except Exception as e:
            filtered.append(original_line + f" # Erreur: {str(e)}")
    
    return '\n'.join(filtered)

def clean_flight_text(flight_data):
    """
    Nettoie le texte d'itinéraire en ne gardant que les lignes de vol principales.
    """
    cleaned_lines = []
    lines = flight_data.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Ignorer les lignes vides
        if not line:
            cleaned_lines.append('')
            i += 1
            continue
        
        # Vérifier si c'est une ligne de vol principale
        is_flight_line = False
        
        # Critère 1: Commence par un numéro suivi d'un code airline
        if re.match(r'^\d+\s+[A-Z0-9]{2}', line):
            is_flight_line = True
        
        # Critère 2: Contient une date (JJMMM) et une paire d'aéroports (6 lettres)
        has_date = re.search(r'\d{2}[A-Z]{3}', line)
        has_airport_pair = re.search(r'[A-Z]{6}', line)
        
        if has_date and has_airport_pair:
            # Vérifier que c'est bien une ligne de vol et non une remarque
            parts = line.split()
            if len(parts) >= 6:  # Doit avoir au moins 6 éléments
                # Vérifier la structure typique: [num] code_airline num_vol ... date jour aéroports
                if (re.match(r'^\d+$', parts[0]) and 
                    re.match(r'^[A-Z0-9]{2}$', parts[1]) and
                    re.match(r'^\d+$', parts[2]) and
                    re.search(r'\d{2}[A-Z]{3}', parts[3])):
                    is_flight_line = True
        
        if is_flight_line:
            cleaned_lines.append(line)
            # Ignorer les lignes suivantes qui sont des remarques (elles ne commencent pas par un numéro)
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^\d+\s+', lines[i].strip()):
                i += 1
        else:
            i += 1
    
    return '\n'.join(cleaned_lines)

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
                # Nettoyer flight_data2 avant le filtrage
                cleaned_flight_data2 = clean_flight_text(flight_data2)
                flight_data1 = filter_amadeus_data(cleaned_flight_data2)
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
                    # Nettoyer flight_data2 avant la conversion
                    cleaned_flight_data2 = clean_flight_text(flight_data2)
                    result2 = process_flight_data(cleaned_flight_data2, parse_flight_info_v2)
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