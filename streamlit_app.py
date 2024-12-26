# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched  # Import 'when_matched'
  

# Title for the Streamlit app
st.title(":cup_with_straw: Customize your Smoothie  :cup_with_straw:")

# User input for the name on the smoothie
name_on_order = st.text_input('Name on your smoothie')
st.write("The name on your smoothie will be", name_on_order)

# Establish session with Snowflake
cnx=st.connection("snowflake")
session = cnx.session()

# Get the 'FRUIT_NAME' column from the 'fruit_options' table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Display the data as a dataframe in Streamlit
st.dataframe(my_dataframe.to_pandas(), use_container_width=True)  # Convert to pandas DataFrame for Streamlit display

# Multiselect widget for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),  # Convert to list for multiselect
    max_selections=5  # Limit to 5 selections
)

if ingredients_list:
    # Join selected ingredients into a comma-separated string
    ingredients_string = ', '.join(ingredients_list)

# Button to submit the order
time_to_insert = st.button('Submit Order')

if time_to_insert and ingredients_list:
    # Correct approach: Format the ingredients list directly into the query
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Debugging: Display the insert statement
    st.write(my_insert_stmt)
    
    # Execute the query
    session.sql(my_insert_stmt).collect()  # Run the SQL command
    
    # Success message
    st.success('Your Smoothie is ordered!', icon="✅")

# Assuming the DataFrame with updates is editable_df, proceed with the merge
if 'editable_df' in locals() and editable_df is not None:
    # Define the original dataset and the edited dataset
    og_dataset = session.table("smoothies.public.orders")
    edited_dataset = session.create_dataframe(editable_df)

    # Perform the merge to update the 'ORDER_FILLED' column
    og_dataset.merge(
        edited_dataset,
        (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
        [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
    ).collect()  # Execute the merge statement

    # Confirm successful update
    st.success('Orders have been successfully updated!')
