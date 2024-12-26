import streamlit as st
from snowflake.snowpark.functions import col
import requests
 
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
 
st.write(""" Choose the fruits you want in your custom Smoothie! """)
 
# Take the name for the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The Name on your Smoothie will be:', name_on_order)
 
# Get active session from Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
 
# Query the fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
 
# Convert to Pandas DataFrame
pd_df = my_dataframe.to_pandas()
 
# Create a multiselect for users to choose up to 5 ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', pd_df['FRUIT_NAME'].tolist(), max_selections=5
)
 
# Initialize an empty string for ingredients
ingredients_string = ''
 
# If the user selects ingredients
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        # Here, using the fruit name directly for the API request
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        # Display the response data from the API
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)
 
    # Create the SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
 
    # Display the SQL statement (for debugging or review purposes)
    st.write(my_insert_stmt)
 
else:
    # Handle the case where no ingredients are selected
    my_insert_stmt = None
    st.write("Please choose some ingredients.")
 
# Add button to submit the order
if my_insert_stmt:  # Only show the button if the insert statement is valid
    time_to_insert = st.button('Submit Order')
 
    if time_to_insert:
        # Execute the SQL insert statement when the button is pressed
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
