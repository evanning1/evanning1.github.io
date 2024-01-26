from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr

from openai import OpenAI
client = OpenAI(api_key = "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")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/emails')
def emails():
    return render_template('emails.html')

@app.route('/howto')
def howto():
    return render_template('howto.html')

@app.route('/get_emails')
def get_emails():
    age = str(request.args.get('age'))
    occupation = str(request.args.get('occupation'))
    username = str(request.args.get('email'))
    password = str(request.args.get('password'))
    # Update these values with your email server details
    # test yoppyenasia123@gmail.com
    # test rewv aivp cgxv sefo 
    imap_server = 'imap.gmail.com'
    imap_port = 993
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("Inbox")

        # Search for all unseen emails
        status, messages = mail.search(None, "(UNSEEN)")
        # Retrieve email data
        email_list = []

        for num in messages[0].split():
            
            status, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_address = parseaddr(msg.get("From"))[1]

                    email_list.append({
                        "subject": subject,
                        "from": from_address,
                        "date": msg.get("Date"),
                    })

        ordered_emails = []
        systemmessage = "You are an email manager for a " + age + " year old " + occupation + ". Your job is to order the persons inbox by the title, sender, and date of the emails, so that the most important emails for them to read, given their age and occupation, are at the top. Also provide a one sentence explanation at the beginning justifying why the order of the emails is as is."
        usermessage = ""
        index = 1
        for thismsg in email_list:
            usermessage += str(index) + " Title: " + thismsg['subject'] + " Sender: " + thismsg['from'] + " Date recieved: " + thismsg['date'] + "\n"
            index += 1
        
        response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                {"role": "system", "content": systemmessage},
                {"role": "user", "content": usermessage}
                ]
            )
        response = str(response.choices[0].message.content)
        return jsonify({"my_string" : response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


