import os
import smtplib
import logging
from email.message import EmailMessage
from flask import Flask, render_template, request, flash, redirect, url_for
import subprocess
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# Load environment variables
load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def send_email(recipient, subject, body, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = recipient
    msg.set_content(body)

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='audio', subtype='mpeg', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        singer = request.form.get("singer")
        try:
            n_videos = int(request.form.get("n_videos"))
            duration = int(request.form.get("duration"))
        except ValueError:
             flash("Number of videos and duration must be integers.", "error")
             return redirect(url_for("index"))
             
        email = request.form.get("email")

        if not singer or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("index"))

        # Simple email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.", "error")
            return redirect(url_for("index"))

        flash("Processing your request... This may take a few minutes.", "info")
        logging.info("Processing request...")
        
        output_filename = f"{singer.replace(' ', '_')}_mashup.mp3"
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "102353013.py")
        logging.debug(f"Script path: {script_path}")
        
        command = ["python", script_path, singer, str(n_videos), str(duration), output_filename]
        logging.debug(f"Command: {command}")
        
        try:
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logging.debug(f"Working directory: {parent_dir}")
            
            # Using Popen to capture output in real-time if needed, but run is fine for now
            result = subprocess.run(command, cwd=parent_dir, capture_output=True, text=True)
            logging.debug(f"Return code: {result.returncode}")
            logging.debug(f"Stdout: {result.stdout}")
            logging.debug(f"Stderr: {result.stderr}")
            
            if result.returncode != 0:
                logging.error(f"Error creating mashup: {result.stderr}")
                # Combine stdout and stderr for the user as the script uses print() for errors
                error_message = f"{result.stderr}\nOutput: {result.stdout}"
                flash(f"Error creating mashup: {error_message}", "error")
                return redirect(url_for("index"))

            output_path = os.path.join(parent_dir, output_filename)
            logging.debug(f"Output path: {output_path}")
            
            if not os.path.exists(output_path):
                 logging.error("Output file not found.")
                 flash("Mashup generation failed: Output file not found.", "error")
                 return redirect(url_for("index"))
                 
            # Send Email
            email_sent = False
            try:
                logging.info("Sending email...")
                send_email(email, "Your YouTube Mashup is Ready!", f"Here is your mashup of {singer}.", output_path)
                flash(f"Mashup sent to {email} successfully!", "success")
                logging.info("Email sent.")
                email_sent = True
            except Exception as e:
                logging.error(f"Email error: {e}")
                flash(f"Failed to send email: {e}. File saved locally as {output_filename}", "warning")
            
            # Cleanup generated file ONLY if email was sent
            if email_sent and os.path.exists(output_path):
                os.remove(output_path)
                logging.info("Output file removed.")
            elif not email_sent:
                logging.info("Email failed, keeping output file.")

        except subprocess.CalledProcessError as e:
             logging.error(f"Subprocess error: {e}")
             flash(f"Script execution failed.", "error")
        except Exception as e:
             logging.error(f"General error: {e}")
             flash(f"An error occurred: {e}", "error")

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
