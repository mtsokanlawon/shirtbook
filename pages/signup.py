import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from streamlit_gsheets import GSheetsConnection

# Page Title
st.title('SignOut')
st.write("Welcome to SignOut! Sign up to create your signout page.")

# Google Sheets connection (cached for optimization)
@st.cache_resource(ttl=60)
def get_db_data(sheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=sheet_name, ttl=0)

# Function to update data
def update_db_data(sheet_name, updtd_df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet=sheet_name, data=updtd_df )

# Get data from Google Sheets
Users_DB = get_db_data("UsersDB")
Signatures_DB = get_db_data("SignaturesDB")
SOphrase_DB = get_db_data("SOphraseDB")

# Function to capture user data
def get_user_data():
    name = st.text_input('Your name:')
    username = st.text_input('Create Username:', max_chars=20)
    
    if name and username:
        Users_df = pd.DataFrame({
            "name": [name.strip()],
            "username": [username.strip()]
        })
        return Users_df
    return pd.DataFrame()

# Function to verify if the username is valid and unique
def verify_user(Users_df):
    if Users_df.empty:
        return "Incomplete form!"
    
    name = Users_df["name"].values[0]
    username = Users_df["username"].values[0]
    
    if name == '':
        return "Invalid Name!"
    elif username == '':
        return "Invalid Username!"
    elif Users_DB['username'].eq(username).any():
        return "Username unavailable!"
    else:
        return "Success"

# Function to capture the user's signout phrase
def get_signout_phrase():
    return st.text_input('Thank God for your wins!')

# Function to generate a shirt design (word cloud)
def generate_shirt(username):
    db_signatures = Signatures_DB[username]
    default_signature = f'Yah,{username},'  # Default text
    signatures = default_signature + db_signatures.astype(str)
    signatures_cleaned = [str(item) for item in signatures if item != 'nan']

    stopwords = set(STOPWORDS).union({'nan', 'NaN', 'Nan', 'NAN'})
    
    wordcloud = WordCloud(background_color='white', stopwords=stopwords).generate(' '.join(signatures_cleaned))
    st.image(wordcloud.to_array())

# Process user signup data
User_df = get_user_data()

# If valid user data is entered, add the username to Signatures_DB
if not User_df.empty:
    username = User_df['username'].unique()[0]
    Signatures_DB[username] = ""  # Add username to Signatures_DB with empty signatures
    # update Database 

# Display "Sign Up" button and handle signup
if st.button('Sign Up'):
    status_ver = verify_user(User_df)
    
    if status_ver == "Success":
        # Update UsersDB
        Updt_Users = pd.concat([Users_DB, User_df], axis=0, ignore_index=True)
        update_db_data("UsersDB", Updt_Users)
        st.success("Sign up successful! Wait...")
        update_db_data("SignaturesDB", Signatures_DB) # update signatures users.
        st.header('Design Shirt...')

    
    else:
        st.error(status_ver)

# Add the user's signout phrase to SOphraseDB
SignOut_phrase = get_signout_phrase()
if SignOut_phrase:
    signout_df = pd.DataFrame({
        'username': [username],
        'signoutphrase': [SignOut_phrase]
        })
    updt_SOphrases = pd.concat([SOphrase_DB, signout_df], axis=0, ignore_index=True)
    update_db_data("SOphraseDB", updt_SOphrases)
# st.success("SignOut phrase saved!")
# else:
    # st.warning("You can add a SignOut phrase later.")
    # Shirt creation section
    if st.button('Create Shirt', type='primary'):
        # if not User_df.empty:
        generate_shirt(User_df['username'].unique()[0])
        st.write('Share your shirt link on your socials for friends to sign!')
        st.write(f'Your link: https://signout.streamlit.app/, access username:{username}')
        st.page_link('pages/view.py', label='Login to view and download shirt')
        




