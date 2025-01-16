import pandas as pd


def get_cell_content_and_split(filepath, row, col):
    """
    Display the content of a specific cell and split it into 'day' and 'date' components.

    :param filepath: Path to the Excel file
    :param row: Row index (0-based)
    :param col: Column index (0-based)
    """
    try:
        # Load the Excel sheet into a DataFrame
        df = pd.read_excel(filepath, sheet_name=0, engine="openpyxl")

        # Get the content of the specified cell
        cell_content = df.iloc[row, col]

        # Print the value of the cell
        print(f"Content in cell at row {row + 1}, column {col + 1}: {cell_content}")

        # Split the cell content into 'day' and 'date'
        if isinstance(cell_content, str):
            parts = cell_content.split(" ", 1)  # Split into two parts: day and date
            if len(parts) == 2:
                day, date = parts
                print(f"Day: {day}")
                print(f"Date: {date}")
            else:
                print("Content could not be split into day and date.")
        else:
            print("The content is not a string that can be split.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    # Filepath to your Excel file
    filepath = "/home/waribu/workspace/myPython/myTimetable/FINAL_ EXAMINATION TIMETABLE -MAY 2024.xlsx"

    # Call the function to display and split the content of the specified cell (row 1, column 2)
    get_cell_content_and_split(
        filepath, 0, 15
    )  # 0, 1 is the 1st row, 2nd column (0-based indexing)
