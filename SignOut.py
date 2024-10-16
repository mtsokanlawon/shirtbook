import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from streamlit_gsheets import GSheetsConnection

# Optimized caching function for GSheets connection
@st.cache_resource(ttl=30)
def fetch_data(sheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=sheet_name, ttl=0)

# Function to update data
@st.cache_resource(ttl=0)
def update_db_data(sheet_name, updtd_df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet=sheet_name, data=updtd_df )

# Optimized justify function using NumPy and pandas
def justify(a, invalid_val=0, axis=1, side='left'):    
    if invalid_val is np.nan:
        mask = pd.notnull(a)
    else:
        mask = a != invalid_val
    justified_mask = np.sort(mask, axis=axis)
    if (side == 'up') | (side == 'left'):
        justified_mask = np.flip(justified_mask, axis=axis)
    
    out = np.full(a.shape, invalid_val, dtype=object)
    if axis == 1:
        out[justified_mask] = a[mask]
    else:
        out.T[justified_mask.T] = a.T[mask.T]
    
    return out

# Caching Google Sheets data
Signatures_DB = fetch_data("SignaturesDB")
Users_DB = fetch_data("UsersDB")
SOphrase_DB = fetch_data("SOphraseDB")

# Function to handle user input
def get_user_data(name_prompt='Your name?', username_prompt='Create Username:'):
    name = st.text_input(name_prompt)
    username = st.text_input(username_prompt, max_chars=20)
    data = pd.DataFrame({"name": [name], "username": [username]})
    data['name'] = data['name'].str.strip()
    data['username'] = data['username'].str.strip()
    return data

# Function to get friend's signature
def get_frnd_signatures():
    username = st.text_input('Enter friend\'s username:', max_chars=20)
    signature = st.text_input('Signature (make it unique!)', max_chars=20)
    data = {username: [signature]}
    return pd.DataFrame(data)

# Function to validate input
def validate_input(input_data):
    if not input_data.strip():
        st.warning("Input cannot be empty.")
        return False
    return True

# Function to verify signatures
def verify_signatures(Signature_df):
    username = Signature_df.columns[0]
    signature = Signature_df[username].unique()[0]
    if username in Users_DB['username'].unique():
        return f'Successfully signed on {username}!'
    else:
        return f'{username} is not a valid username!'

# Function to generate word cloud
# @st.cache_data
def generate_wordcloud(text):
    stopwords = {'nan', 'NaN', 'Nan', 'NAN'}
    wordcloud = WordCloud(background_color='white', stopwords=stopwords).generate(text)
    return wordcloud.to_array()

# App title and description
st.title(":rainbow[SignOut]")
st.page_link('pages/about.py', label="Welcome to SignOut! Learn :blue[more]")
st.page_link('pages/signup.py', label='click :red[Sign up] to create your signout page')

# Sidebar navigation
with st.sidebar:
    st.header(':rainbow[Navigation]')
    st.page_link('SignOut.py', label=':blue[Home]')
    st.page_link('pages/signup.py', label=':orange[Sign Up]')
    st.page_link('pages/view.py', label=':violet[Login]')
    st.page_link('pages/about.py', label=':violet-background[About]')

# Display user's friend's signature section
st.header(':blue[Sign] :orange[*on*] :violet[*a*] **Friend**:red[!]')
Signature_df = get_frnd_signatures()
if Signature_df.empty:
    st.stop()

username = Signature_df.columns[0]
signature = Signature_df[username].unique()[0]

# Validate and show signature
if validate_input(username) and validate_input(signature):
    st.write(f"Username: {username}, Signature: {signature}")

# Create updated signature DataFrame
Signature_df1 = Signature_df.reindex(columns=Signatures_DB.columns, fill_value=" ")
updt_Signatures = Signatures_DB._append(Signature_df1).reset_index(drop=True)

# Justify the signature DataFrame
arr = justify(updt_Signatures.to_numpy(), invalid_val=np.nan, axis=0)
arr = justify(arr, invalid_val=' ', axis=0)
updt_Signatures = pd.DataFrame(arr, columns=updt_Signatures.columns, index=updt_Signatures.index)

# Button to sign the friend's signature
if st.button('Sign!', type='primary'):
    # conn = st.connection("gsheets", type=GSheetsConnection)
    Signatures_DB = fetch_data("SignaturesDB")
    
    # Verify signature
    signature_ver = verify_signatures(Signature_df)
    
    if signature_ver == f'Successfully signed on {username}!':
        update_db_data("SignaturesDB", updt_Signatures)
        st.success(signature_ver)
        
        updt_SOphrases = fetch_data("SOphraseDB")
        user = username
        db_signatures = updt_Signatures[username]
        def_signature = f'Yah,{user},'  # Default text
        signatures = def_signature + db_signatures.astype(str)
        signatures_cleaned = [str(item) for item in signatures if item is not None]
        
        # Generate and display word cloud
        signoutphrase = updt_SOphrases[updt_SOphrases['username'] == user]['signoutphrase'].unique()[0]
        st.write(f"{username}: ... {signoutphrase}")
        wordcloud_image = generate_wordcloud(' '.join(signatures_cleaned))
        st.image(wordcloud_image)
    
    else:
        st.error(signature_ver)
