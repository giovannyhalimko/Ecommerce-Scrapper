import tkinter as tk
from tkinter import messagebox, ttk
import os
import pandas as pd
import threading
import webbrowser
import matplotlib.pyplot as plt
matplotlib.use('agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui_scrapper.blibli import scrape_blibli
from ui_scrapper.bukalapak import scrape_bukalapak
from ui_scrapper.tokopedia import scrape_tokopedia

scale_var = None
search_entry = None
is_tokopedia_checked = None
is_blibli_checked = None
is_bukalapak_checked = None


# Define a function to create and display the loading screen with a progress bar
def show_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Loading...")
    
    # Calculate the position to center the loading screen on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    loading_screen_width = 400  # Adjust the width of the loading screen if needed
    loading_screen_height = 200  # Adjust the height of the loading screen if needed
    x = (screen_width - loading_screen_width) // 2
    y = (screen_height - loading_screen_height) // 2
    
    loading_screen.geometry(f"{loading_screen_width}x{loading_screen_height}+{x}+{y}")
    
    loading_label = tk.Label(loading_screen, text="Loading, please wait...")
    loading_label.pack(padx=20, pady=10)
    progress_bar = ttk.Progressbar(loading_screen, orient='horizontal', length=200, mode='indeterminate')
    progress_bar.pack(padx=20, pady=10)
    progress_bar.start()

    # Grab the focus to the loading screen, disabling interaction with the main form
    loading_screen.grab_set()
    
    return loading_screen, progress_bar

def display_search_results():
    # Hide the main form
    hide_main_form()

    # Get a list of all ".xlsx" files in the "./ui_data" directory
    excel_files = [f for f in os.listdir("./ui_data") if f.endswith(".xlsx")]

    if not excel_files:
        messagebox.showinfo("Info", "No Excel files found in the './ui_data' directory")
        return

    try:
        height = 0
        for excel_file in excel_files:
            file_path = os.path.join("./ui_data", excel_file)
            file_name = os.path.splitext(excel_file)[0]
            if file_name == "tokopedia":
                if is_tokopedia_checked.get() == 0:
                    continue

            if file_name == "blibli":
                if is_blibli_checked.get() == 0:
                    continue

            if file_name == "bukalapak":
                if is_bukalapak_checked.get() == 0:
                    continue

            df = pd.read_excel(file_path)

            table_position = tk.Frame(root)
            table_position.place(x=screen_width / 110, y=screen_height / 100 + height)

            # Add a label with the file name above each table
            file_label = tk.Label(table_position, text=f"File: {excel_file}")
            file_label.place(x=20, y=0)
            
            # Display the data in a table format (you can use a Ttk Treeview widget for this)
            # Here's a simple example:
            result_table = ttk.Treeview(table_position, height=13)
            result_table["columns"] = tuple(df.columns[:-1])
            result_table["show"] = "headings"
            for col in df.columns[:-1]:
                result_table.heading(col, text=col)
                result_table.column(col, width=160)
            for index, row in df.iterrows():
                result_table.insert("", "end", values=tuple(row[:-1]) )
                result_table.bind("<Double-1>", lambda e: webbrowser.open_new(e.widget.item(e.widget.selection())['values'][7]))
            result_table.pack(padx=20, pady=20)

            height += 320

        # Add a button to display the main form again
        display_form_button = tk.Button(root, text="Search Again", command=display_main_form)
        display_form_button.place(x=screen_width - 100, y = 10)

        render_statistics()
        
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the Excel file: {e}")

def render_statistics():
    statistic_position = tk.Frame(root)
    statistic_position.place(x=screen_width / 110 * 73, y=screen_height / 100 * 4)

    # Add a label with the file name above each table
    file_label = tk.Label(statistic_position, text="Statistics")
    file_label.pack()

    # read all excels file
    excel_files = [f for f in os.listdir("./ui_data") if f.endswith(".xlsx")]

    data = []
    # Your calculated data for visualization
    average_prices = []
    categories = []

    # Initialize lists to store statistics for each file
    total_data_list = ["Total Data"]
    average_price_list = ["Average Price"]
    max_price_list = ["Max Price"]
    min_price_list = ["Min Price"]
    average_rating_list = ["Average Rating"]
    max_rating_list = ["Max Rating"]
    min_rating_list = ["Min Rating"]

    # render statistics for each file
    for excel_file in excel_files:
        file_path = os.path.join("./ui_data", excel_file)
        file_name = os.path.splitext(excel_file)[0]

        if file_name == "tokopedia":
            if is_tokopedia_checked.get() == 0:
                continue

        if file_name == "blibli":
            if is_blibli_checked.get() == 0:
                continue

        if file_name == "bukalapak":
            if is_bukalapak_checked.get() == 0:
                continue

        df = pd.read_excel(file_path)

        categories.append(file_name)

        # Count total data
        total_data = len(df.index)
        total_data_list.append(total_data)

        # Count average price
        average_price = df['Price'].mean()
        average_price_list.append(average_price)
        average_prices.append(average_price)

        # Count max price
        max_price = df['Price'].max()
        max_price_list.append(max_price)

        # Count min price
        min_price = df['Price'].min()
        min_price_list.append(min_price)

        # Count average rating
        average_rating = df['Rating'].mean()
        average_rating_list.append(average_rating)

        # Count max rating
        max_rating = df['Rating'].max()
        max_rating_list.append(max_rating)

        # Count min rating
        min_rating = df['Rating'].min()
        min_rating_list.append(min_rating)

    # Append all the lists to the data list
    data.extend([
        total_data_list,
        average_price_list,
        max_price_list,
        min_price_list,
        average_rating_list,
        max_rating_list,
        min_rating_list
    ])

    # Create a Treeview widget
    tree = ttk.Treeview(statistic_position, columns=("metric", "blibli", "bukalapak", "tokopedia"), show='headings')

    # Define the column headings
    tree.heading("metric", text="Metric")
    tree.heading("blibli", text="blibli.xlsx")
    tree.heading("bukalapak", text="bukalapak.xlsx")
    tree.heading("tokopedia", text="tokopedia.xlsx")

    # Define column widths
    tree.column("metric", width=120)
    tree.column("blibli", width=120)
    tree.column("bukalapak", width=150)
    tree.column("tokopedia", width=150)

    # Insert the data into the Treeview
    for row in data:
        tree.insert("", "end", values=row)

    # Pack the Treeview into the window
    tree.pack()

    # Create a frame for the chart
    chart_frame = tk.Frame(statistic_position)
    chart_frame.pack(side=tk.LEFT, padx=20, pady=20)

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the bar chart
    ax.bar(categories, average_prices, color=['blue', 'green', 'red'])
    ax.set_xlabel('Files')
    ax.set_title('Average Price Comparison')

    # Add the figure to the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def search():
    global scale_var, search_entry, is_tokopedia_checked, is_blibli_checked, is_bukalapak_checked

    # Disable the main form
    root.withdraw()

    # Function to perform search
    search_query = search_entry.get()
    if search_query == "":
        messagebox.showerror("Error", "Please enter a search query")
        root.deiconify()  # Re-enable the main form
        return

    page = scale_var.get()
    
    # Validate if non of the checkboxes are checked
    if is_tokopedia_checked.get() == 0 and is_blibli_checked.get() == 0 and is_bukalapak_checked.get() == 0:
        messagebox.showerror("Error", "Please select between Tokopedia, Blibli, or Bukalapak or all of them")
        root.deiconify()  # Re-enable the main form
        return

    # Create a list of tuples with the scraping functions and their arguments
    scraping_tasks = []

    if is_tokopedia_checked.get() == 1:
        scraping_tasks.append((scrape_tokopedia, (page, search_query)))
    if is_blibli_checked.get() == 1:
        scraping_tasks.append((scrape_blibli, (page, search_query)))
    if is_bukalapak_checked.get() == 1:
        scraping_tasks.append((scrape_bukalapak, (page, search_query)))

    # Create and display the loading screen with a progress bar
    loading_screen, progress_bar = show_loading_screen()

    # Define a function to execute each scraping task in a separate thread
    def execute_scraping_tasks():
        for task in scraping_tasks:
            scraping_function, args = task
            scraping_thread = threading.Thread(target=scraping_function, args=args)
            scraping_thread.start()
            scraping_thread.join()  # Wait for each thread to finish before moving to the next

        # Close the loading screen after all tasks are finished
        loading_screen.destroy()
        root.deiconify()  # Re-enable the main form

        # Display the search results
        display_search_results()

    # Start executing the scraping tasks in a separate thread
    threading.Thread(target=execute_scraping_tasks).start()

def hide_main_form():
    # Hide the main form
    for widget in root.winfo_children():
        widget.destroy()

def display_main_form():
    hide_main_form()

    global scale_var, search_entry, is_tokopedia_checked, is_blibli_checked, is_bukalapak_checked

    # Calculate the coordinates for centering the search bar
    x = (screen_width - 400) / 2  # Assuming the search bar width is 400
    y = (screen_height - 100) / 2  # Assuming the search bar height is 100

    # Create a frame to hold the checkboxes
    checkbox_frame = tk.Frame(root)
    checkbox_frame.place(x=x, y=y-75)

    # Create the checkboxes with labels
    is_tokopedia_checked = tk.IntVar()
    tokopedia_checkbox = tk.Checkbutton(checkbox_frame, text="Tokopedia", variable=is_tokopedia_checked)
    tokopedia_checkbox.pack(side=tk.LEFT, padx=5)

    is_blibli_checked = tk.IntVar()
    blibli_checkbox = tk.Checkbutton(checkbox_frame, text="Blibli", variable=is_blibli_checked)
    blibli_checkbox.pack(side=tk.LEFT, padx=5)

    is_bukalapak_checked = tk.IntVar()
    bukalapak_checkbox = tk.Checkbutton(checkbox_frame, text="Bukalapak", variable=is_bukalapak_checked)
    bukalapak_checkbox.pack(side=tk.LEFT, padx=5)

    page_input_frame = tk.Frame(root)
    page_input_frame.place(x=x, y=y-45)

    # Create a label for the scale widget
    scale_label = tk.Label(page_input_frame, text="Pages to fetch : ")
    scale_label.pack(side=tk.LEFT, padx=(0, 5))  

    # Create a scale widget for input range
    scale_var = tk.IntVar()
    scale = tk.Scale(page_input_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=scale_var)
    scale.pack(side=tk.LEFT, padx=(0, 5))  # Add right padding to separate from checkbox

    # Create a frame to hold the search bar
    frame = tk.Frame(root)
    frame.place(x=x, y=y)

    # Create a label for the search bar
    search_label = tk.Label(frame, text="Enter your search query:")
    search_label.pack()

    # Create an entry widget for the search query
    search_entry = tk.Entry(frame, width=80)
    search_entry.pack(pady=10)

    # Create a search button
    search_button = tk.Button(frame, text="Search", command=search)
    search_button.pack(pady=10)


# Create the Tkinter window
root = tk.Tk()

# Set the title of the window
root.title("Giovanny Halimko")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the window size to the screen size
root.geometry(f"{screen_width}x{screen_height}")

# display main form
display_main_form()

# Run the Tkinter event loop
root.mainloop()