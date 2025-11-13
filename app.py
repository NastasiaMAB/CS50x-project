import io
import csv
import pandas as pd
import numpy as np
import plotly.express as px


from flask import Flask, flash, jsonify, redirect, render_template, request, session


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Ensure file was submitted
        if not request.files.get("csvfile"):
            return jsonify({"error": "file is missing"})

        # Check the uploaded file is a csv file
        csv_file_c = request.files.get("csvfile")
        if csv_file_c.content_type != "text/csv":
            return jsonify({"error": "file is not a csv file"})

        # Decode the file content to a string
        csv_file = io.TextIOWrapper(csv_file_c, encoding='utf-8')

        # Access form data
        read_data = []
        user_data = csv.DictReader(csv_file)
        for row in user_data:
            read_data.append(row)

        # Check csv file has at least 2 columns
        if len(user_data.fieldnames)<2:
            return jsonify({"error": "csv file has less than 2 columns"})

        # Check csv file has no more than three columns
        if len(user_data.fieldnames)>3:
            return jsonify({"error": "csv file has more than 3 columns"})

        # If csv file has 2 columns check the second column is only numerical or empty
        if len(user_data.fieldnames)==2:
            for row in read_data:
                try:
                    if row[user_data.fieldnames[1]] == '':
                        continue
                    float(row[user_data.fieldnames[1]])
                except ValueError:
                    return jsonify({"error": "csv file second column has some features not numerial"})

        # If csv file has 3 columns check the third column is only string and the third column is only numerical or empty
        if len(user_data.fieldnames)==3:
            for row in read_data:
                try:
                    if row[user_data.fieldnames[2]] == '':
                        continue
                    float(row[user_data.fieldnames[2]])
                except ValueError:
                    return jsonify({"error": "csv file third column has some features not numerial"})

        # Load the data as dataframe
        df=pd.DataFrame(read_data)

        # Drop missing values
        df.replace("", np.nan, inplace=True)
        df.dropna(inplace=True)

        # If user data has 3 columns
        if len(user_data.fieldnames)==3:

            # Extract the column names
            col2=df.columns[1]
            col3=df.columns[2]

            # Convert to float
            df[col3] = df[col3].astype(float)

            # Get the summary statistic of the numerical features
            stat = df.describe()
            stat_html = stat.to_html()

            # Get the summary statistics of the numerical feature by group
            stat2 = df.groupby(col2)[col3].describe()
            stat_html2 = stat2.to_html()

            # Convert the dataframes with stat summary to a csv string
            stat_save = stat.to_csv(index=True, header=True)
            stat_save2 = stat2.to_csv(index=True, header=True)

            # Make a boxplot using the numerical data
            fig = px.box(df, x=col2, y=col3)

            # Convert the plot to HTML
            fig_html = fig.to_json()

            # Return image and stat on thw webpage
            return jsonify(fig_html=fig_html, stat_html=stat_html, stat_html2=stat_html2, stat_save=stat_save, stat_save2=stat_save2)

        # If user data has 3 columns
        if len(user_data.fieldnames)==2:

            # Extract the column names
            col2=df.columns[1]
            # Convert to float
            df[col2] = df[col2].astype(float)

            # Get the summary statistic of the numerical features
            stat = df.describe()
            stat_html = stat.to_html()

            # Convert the dataframes with stat summary to a csv string
            stat_save = stat.to_csv(index=True, header=True)

            # Make a boxplot using the numerical data
            fig = px.box(df, y=col2)

            # Convert the plot to HTML
            fig_html = fig.to_json()

            # Return image and stat on thw webpage
            return jsonify(fig_html=fig_html, stat_html=stat_html, stat_save=stat_save)

    else:

        # Render app homepage
        return render_template("index.html")


