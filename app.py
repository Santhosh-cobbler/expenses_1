from flask import Flask, render_template, request, redirect, url_for, session
import supabase
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# import the .env file
load_dotenv()

app = Flask(__name__)

SUPABASE_URL=os.getenv('SUPABASE_URL')
SUPABASE_KEY=os.getenv('SUPABASE_PUBLISHABLE_KEY')


#secret-key
app.secret_key = "supersecretkey"


supabase: Client = create_client(
    SUPABASE_URL, SUPABASE_KEY
)

''' 
    first it goes to register
    but you need to rewirte thee code afte rthe production
'''

#swichboard
@app.route('/')
def switchborad():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    return redirect(url_for('login'))


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        # supabase going to create the new user
        response = supabase.auth.sign_up({
                "email": email,
                "password": password
            }
        )

        if response.user:
            return(redirect(url_for('login')))
        
        else:
            return "Registration Failed"

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Authenticate with Supabase
            data = supabase.auth.sign_in_with_password({
                "email":email,
                "password": password
            })

            # saves the session id in the server
            session['user_id'] = data.user.id

            return redirect(url_for('home'))
        
        except Exception as e:
            return f'Login failed: {str(e)}'
        
    
    return render_template('login.html')


@app.route('/home',methods=['GET','POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form.get('date')
        category = request.form.get('category')
        file = request.form.get('file-name')

        response = supabase.table('vault_entries').insert({
            "user_id": session['user_id'],
            "entry_date": date,
            "category": category,
            "file_name":file
        }).execute()

        return render_template('index.html')
        

    return render_template('index.html')

@app.route('/view-db')
def view():
    # checks the user_id in session
    if 'user_id' not in session:
        return redirect(url_for('login'))


    # if the session is there then it might be send data to the html file
    response = supabase.table('vault_entries').select('*').eq('user_id',session['user_id']).execute()
    
    #extract the list of row in correct format
    entries = response.data
    print(entries)

    return render_template('view.html', entries=entries)


if __name__ == '__main__':
    app.run(debug=True)