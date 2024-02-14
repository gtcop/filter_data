import pandas as pd 
import streamlit as st

def company_name_approch():

    # Function to convert data to lowercase
    def convert_to_lowercase(data):
        data.columns = data.columns.str.lower()   # Convert column names to lowercase
        data = data.apply(lambda x: x.astype(str).str.lower())   # Convert all data to lowercase
        return data

    # Function to process files
    def process_files(camp_file, all_clients):
        df_s1 = camp_file  # Read the campaign file 
        df1 = all_clients   # Read the all clients file

        # Create new columns
        df_s1['status'] = 'na'
        df_s1['reason'] = 'na'
        df_s1['match_reason'] = 'na'
        df_s1['match_condition'] = 'na'

        df_s1['original_index'] = df_s1.index      # Create a new column to store original indices
        
        for i in range(len(df_s1)):        # Iterate through the indices of the two DataFrames
            match_found = False
            matching_reasons = []
            matching_word_df1 = 'na'  # Variable to store the actual matching word from df1

            # Check for exact row match
            if any(df_s1.iloc[i]['company name'] == df1.iloc[j]['company name'] for j in range(len(df1))):
                df_s1.at[i, 'status'] = 'matched'
                match_found = True
                matching_word_df1 = df1[df1['company name'] == df_s1.iloc[i]['company name']]['company name'].iloc[0]

            if matching_reasons:
                df_s1.at[i, 'reason'] = ', '.join(matching_reasons)
                df_s1.at[i, 'match_reason'] = matching_word_df1  # Use the actual matching word from df1

        # Sort the DataFrame based on the original indices
        df_s1 = df_s1.sort_values(by='original_index').reset_index(drop=True)
        
        return df_s1


    # Function to convert first name to title case
    def convert_first_name_in_title_case(data):
        data['first name'] = data['first name'].apply(lambda x: x.title())  # Convert first name to title case
        return data

    # Main function
    def main_2():
        st.title("Filter file by company name")

        # Upload campaign file
        camp_file = st.sidebar.file_uploader("Upload Campaign File (CSV)", type=['csv'])
        if camp_file is not None:
            camp_data = pd.read_csv(camp_file)
            st.write("Campaign File Preview:")
            st.write(camp_data.head())

            # Upload all clients file
            all_clients = st.sidebar.file_uploader("Upload All Clients File (CSV)", type=['csv'])
            if all_clients is not None:
                all_clients_data = pd.read_csv(all_clients)
                st.write("All Clients File Preview:")
                st.write(all_clients_data.head())

                # Process files
                processed_data = process_files(convert_to_lowercase(camp_data), convert_to_lowercase(all_clients_data))
                # st.write("Processed Data:")
                # st.write(processed_data)

                # Convert first name to title case
                processed_data = convert_first_name_in_title_case(processed_data)
                st.write("Processed Data with First Name in Title Case:")
                st.write(processed_data)

    if __name__ == "__main__":
        main_2()

st.set_page_config(page_title="Data Processing Streamlit App", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Data Processing Streamlit App (launch campaign)")

approach = st.sidebar.selectbox("Choose approach", ("Email Approach", "Company Name Approach"))
if approach == "Email Approach":
    # Execute email approach
    email_approch()
elif approach == "Company Name Approach":
    # Execute company name approach
    company_name_approch()
