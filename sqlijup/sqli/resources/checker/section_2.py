#!/usr/bin/python3
import requests
import subprocess
import sys
import mysql.connector
import os

# Function to execute the student's SQL queries and return results.
def execute_query(query):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='practice'
        )
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        cursor.close()
        return result

    except mysql.connector.Error as e:
        print(f"Error executing SQL query: {e}")
        sys.exit(4)

def main():
    # Check to make sure that the function is called correctly.
    if (len(sys.argv) != 3):
        print("Usage: ./section_2.py <step_num> <query>")
        sys.exit(2)

    step = sys.argv[1]
    query = sys.argv[2]

    # Make sure that the step number is between 12 and 14.
    if (int(step) >= 12 and int(step) <= 14):
        # Reset the database for this step.
        subprocess.run("/home/.checker/reset_db.py " + step, shell=True)

        # Construct the POST request to php_practice.php.
        url = 'http://localhost/php_practice.php'
        data = {
            'student_id': query
        }
        response = requests.post(url, data=data)

        # Only proceed if the request was successful.
        if (response.status_code == 200):
            # Check if the response file for this step already exists.
            answer_file = f"/home/.checker/responses/step_{step}_answer.txt"
            # Checks to see if the student already answered this correctly.
            if os.path.exists(answer_file):
                # If it does, check if $conn->prepare($sql) is in php_practice.php.
                # This is the only "check" that will be done to make sure that the file was already patched.
                # A lazy approach, but good enough.
                with open("/var/www/html/php_practice.php", "r") as php_file:
                    php_content = php_file.read()
                    if "$conn->prepare($sql)" in php_content:
                        # If the file is indeed patched, exit with 3.
                        sys.exit(3)

                # Otherwise, they haven't gotten that far yet. Set the query equal to their supposed
                # response. Continue with the rest of the check.
                # sys.exit(1)

            # If we get here, the response file does NOT exist yet. So, we continue with our normal logic.
            # Write the server’s response to the new step response file
            with open(answer_file, "w+") as f:
                # Remove the HTML form by splitting on <!--.
                removed_prompt = (response.text).split("<!--")[0]
                f.write(removed_prompt)

            # Decide what rows we expect based on the step.
            expected_rows = []
            if (step == "12"):
                expected_rows = [
                    (100, 'Taylor', 'B'),
                    (101, 'Danny', 'B'),
                    (102, 'Hannah', 'D'),
                ]
            elif (step == "13"):
                expected_rows = [
                    (100, 'Taylor', 'B'),
                    (101, 'Danny', 'B'),
                    (102, 'Hannah', 'B'),
                ]
            elif (step == "14"):
                expected_rows = [
                    (100, 'Taylor', 'B'),
                    (101, 'Danny', 'B'),
                    (102, 'Hannah', 'B'),
                    (200, 'Jason', 'F')
                ]

            # Get what's in the DB after the student's query.
            actual_results = execute_query("SELECT * FROM students")

            # Compare.
            if (actual_results == expected_rows):
                # If this was the correct response, AND their second statement properly updated the table, we return 
                # True, then write their response to a file to save their work.
                with open(answer_file, "w+") as f:
                    removed_prompt = (response.text).split("<!--")[0]
                    f.write(removed_prompt)
                sys.exit(0)
            else:
                sys.exit(1)

if __name__ == "__main__":
    main()
