import csv

def find_timetable_entry(timetable, date, time, room, unit_code, day):
    for entry in timetable:
        if ('date' in entry and entry['date'] == date and
            'time' in entry and entry['time'] == time and
            'room' in entry and entry['room'] == room and
            'unit_code' in entry and entry['unit_code'] == unit_code and
            'day' in entry and entry['day'] == day):
            return entry
    return None

def load_timetable_from_csv(file_path):
    timetable = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            timetable.append(row)
    return timetable

def main():
    timetable = load_timetable_from_csv('Timetable.csv')
    
    date = '13/08/2024'
    time = '1'
    room = ''
    unit_code = ''
    day = 'Tuesday'
    
    result = find_timetable_entry(timetable, date, time, room, unit_code, day)
    if result:
        print("Timetable entry found:", result)
    else:
        print("Timetable entry not found")

if __name__ == "__main__":
    main()