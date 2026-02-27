import os
import csv

class BoardPinsHelper:
    # Define the expected fields in the CSV files
    CSV_FIELDS = [
        'board_id', 'pin_number', 'pin_name', 'default_function',
        'schematic', 'silkscreen', 'soc', 'gpio_number',
        'alt0', 'alt1', 'alt2', 'alt3', 'pinctrl_section',
        'pinctrl_psel', 'dts_section', 'dts_key',
        'dts_prop', 'dts_bank', 'dts_pin', 'dts_mode',
        'dts_label', 'dts_code', 'dts_aliases',
        'ol_pinctrl_section', 'ol_pinctrl_psel', 'ol_section',
        'ol_key', 'ol_prop', 'ol_bank', 'ol_pin', 'ol_mode',
        'ol_label', 'ol_code', 'ol_aliases'
    ]

    COMMON_BOARD_MAPPINGS = {
        'brd2911a': 'veda_sl917_explorer',
    }

    def __init__(self, csv_path):
        self.boards = {}

        # Find all of the CSV files in the csv_path directory tree
        for root, dirs, files in os.walk(csv_path):
            for file in files:
                if file.endswith('.csv'):
                    csv_file = os.path.join(root, file)
                    lines = self._read_csv_file(csv_file)
                    if lines:
                        pin_list = self._build_pin_list(lines)
                        if pin_list:
                            board_id = pin_list[0].get('board_id', 'unknown_board')

                            # Filter the pin list to only include pins that have a non-empty 'ol_label' field
                            pin_list = [pin['ol_label'] for pin in pin_list if pin.get('ol_label', '').strip()]

                            # Flatten the list of pin labels into a single list of strings
                            pin_labels = [ item.strip() for entry in pin_list for item in entry.split(',') if item.strip() ]

                            self.boards[board_id] = pin_labels

    def _read_csv_file(self, csv_file):
        lines = None
        try:
            with open(csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                lines = [row for row in reader]
        except FileNotFoundError:
            print(f"Error: The file {csv_file} does not exist.")
        return lines

    def _build_pin_list(self, lines):
        pin_list = []
        # Process each line of the .csv file, skipping the header line
        for i, line in enumerate(lines):
            if i == 0:
                continue  # Skip header line
            pin_dict = {}

            # Skip lines that do not have at least 2 columns (board_id and pin_number)
            if len(line) < 2:
                continue

            for j, field in enumerate(self.CSV_FIELDS):
                if j < len(line):
                    pin_dict[field] = line[j].strip()
                else:
                    pin_dict[field] = ""

            # Skip pins that do not have a label or are common power pins
            # like GND, 3V3, 5V, VBATT, VCC
            pin_excluded = pin_dict.get('pin_name', '').lower() in ['gnd', '3v3', '5v', 'vbatt', 'vcc']
            if pin_excluded or pin_dict.get('ol_label', '').strip() == "":
                continue
            pin_list.append(pin_dict)

        return pin_list

    def get_pins_for_board(self, board_id: str):
        # Remap common board names to match the CSV files
        board_id = self.COMMON_BOARD_MAPPINGS.get(board_id, board_id)
        
        # Check for exact match first
        if board_id in self.boards:
            return self.boards[board_id]

        # Prefix match
        matches = [ key for key in self.boards if key.startswith(board_id + '_')]
        if len(matches) == 1:
            return self.boards[matches[0]]

        # Failure cases
        if len(matches) > 1:
            raise ValueError(f"Multiple boards match the prefix '{board_id}': {matches}")
        raise ValueError(f"No board found with id '{board_id}'")
