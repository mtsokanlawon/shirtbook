import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from streamlit_gsheets import GSheetsConnection


def get_db_data(sheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=sheet_name)

# Get login data from the user

def get_login_data():
    name = st.text_input('Enter your name')
    username = st.text_input('Enter username:', max_chars=20)
    
    data = {
        "name": [name],
        "username": [username],
    }
    
    Users_df = pd.DataFrame(data)
    Users_df['name'] = Users_df['name'].str.strip()
    Users_df['username'] = Users_df['username'].str.strip()  # Fixed typo here

    return Users_df

# Verify the login credentials
def verify_login():
    name = df["name"].unique()[0]
    username = df["username"].unique()[0]
    reconn = st.connection("gsheets", type=GSheetsConnection)
    Users_DBupdtd = reconn.read(worksheet="UsersDB")

    # Verify the login details
    if not Users_DBupdtd.query('username == @username and name == @name').empty:
        return "Login Successful"
    else:
        return "Invalid name or username!"

st.title('SignOut Shirt')
st.write('Provide your details to view your shirts. ensure you signed up! reload page if failed.')
df = get_login_data()

if st.button('Login'):
    # conn = st.connection("gsheets", type=GSheetsConnection)

    # Read Google Sheets data
    Users_DB = get_db_data("UsersDB")
    Signatures_DB = get_db_data("SignaturesDB")
    SOphrase_DB = get_db_data("SOphraseDB")

    status_ver = verify_login()

    if status_ver == "Login Successful":
        st.success(status_ver)
        user = df['username'].unique()[0]
        db_signatures = Signatures_DB[user]
        
        # Prepare signatures for word cloud
        def_signature = 'Yah,' + user + ','  # Default text
        signatures = def_signature + db_signatures.astype(str)
        signatures_cleaned = [str(item) for item in signatures if item is not None and item != 'nan']

        stopwords = set(STOPWORDS).union({'nan', 'NaN', 'Nan', 'NAN'})

        # Generate word cloud
        wordcloud = WordCloud(background_color='white', stopwords=stopwords).generate(' '.join(signatures_cleaned))
        wordcloud.to_file('wordcloud.png')  # Save the word cloud image
        st.write(SOphrase_DB[SOphrase_DB['username'] == user]['signoutphrase'].unique()[0])
        st.image('wordcloud.png')

        # Share shirt link
        shirt_link = f'https://signout.streamlit.app/'
        st.write(f'Share your shirt link on your socials for friends to sign!')
        st.write(f'Your link is {shirt_link}, access username: \'{user}\'')

        # Allow the user to download the word cloud image
        with open("wordcloud.png", "rb") as file:
            st.download_button(
                label="Download image",
                data=file,
                file_name=f"{user}signout_shirt.png",
                mime="image/png",
            )

    else:
        st.error(status_ver)
