import streamlit as st
import pandas as pd

# Function to convert data to lowercase
def convert_to_lowercase(data):
    data.columns = data.columns.str.lower()   # Convert column names to lowercase
    data = data.apply(lambda x: x.astype(str).str.lower())   # Convert all data to lowercase
    return data

# Function to calculate percentage match between two strings
def calculate_percentage_match(word1, word2):
    longer_word_length = max(len(word1), len(word2))
    common_length = sum(c1 == c2 for c1, c2 in zip(word1, word2))
    return (common_length / longer_word_length) * 100

# Function to process files
def process_files(camp_file, all_clients):
    df_s1 = camp_file  # Read the campaign file 
    df1 = all_clients   # Read the all clients file

    # Create new columns
    df_s1['status'] = 'na'
    df_s1['reason'] = 'na'
    df_s1['match_percentage'] = 70.0
    df_s1['match_reason'] = 'na'
    df_s1['match_condition'] = 'na'

    # Set the match thresholds
    whole_row_match_threshold = 100  # Check for exact row match
    word_match_threshold = 70  # Check for at least 70% word match

    df_s1['original_index'] = df_s1.index      # Create a new column to store original indices
    
    for i in range(len(df_s1)):        # Iterate through the indices of the two DataFrames

        match_found = False
        matching_reasons = []
        max_match_percentage = 100.0
        match_condition = 'na'
        matching_word_df1 = 'na'  # Variable to store the actual matching word from df1

        # Check for exact row match
        if any(df_s1.iloc[i]['company name'] == df1.iloc[j]['company name'] for j in range(len(df1))):
            df_s1.at[i, 'status'] = 'matched'
            match_found = True
            match_condition = 'full_word_match'
            matching_word_df1 = df1.iloc[j]['company name']

        # If the whole row match failed, check for other conditions
        if not match_found:
            for j in range(len(df1)):
                # Get the first two words of each row in 'company name' column
                words_df_s1 = df_s1['company name'].iloc[i].split()[:2]
                words_df1 = df1['company name'].iloc[j].split()[:2]

                # Check if the first word matches
                if words_df_s1[0] == words_df1[0]:
                    df_s1.at[i, 'status'] = 'matched'
                    match_found = True
                    matching_reasons.append(words_df1[0])
                    match_condition = 'first_word_match'
                    matching_word_df1 = df1.iloc[j]['company name']

                # Check if the second word matches
                elif len(words_df_s1) > 1 and len(words_df1) > 1 and words_df_s1[1] == words_df1[1]:
                    df_s1.at[i, 'status'] = 'matched'
                    match_found = True
                    matching_reasons.append(words_df1[1])
                    match_condition = 'second_word_match'
                    matching_word_df1 = df1.iloc[j]['company name']

                # Check if at least 70% of words match
                else:
                    for word_df_s1 in words_df_s1:
                        for word_df1 in words_df1:
                            percentage_match = calculate_percentage_match(word_df_s1, word_df1)
                            if percentage_match >= word_match_threshold:
                                df_s1.at[i, 'status'] = 'matched'
                                match_found = True
                                matching_reasons.append(word_df1)
                                match_condition = 'percentage_match'
                                # Update the maximum match percentage if needed
                                max_match_percentage = max(max_match_percentage, percentage_match)
                                matching_word_df1 = df1.iloc[j]['company name']

        if matching_reasons:
            df_s1.at[i, 'reason'] = ', '.join(matching_reasons)
            df_s1.at[i, 'match_percentage'] = max_match_percentage
            df_s1.at[i, 'match_reason'] = matching_word_df1  # Use the actual matching word from df1
            df_s1.at[i, 'match_condition'] = match_condition

    # Sort the DataFrame based on the original indices
    df_s1 = df_s1.sort_values(by='original_index').reset_index(drop=True)
    usefull_cols = ["company name", "first name", "email", "status","reason","match_reason"]
    df_s1 = df_s1[usefull_cols]
    return df_s1

# Function to convert first name to title case
def convert_first_name_in_title_case(data):
    data['first name'] = data['first name'].apply(lambda x: x.title())  # Convert first name to title case
    return data

# Main function
def main():
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
            st.write("Processed Data:")
            st.write(processed_data)

            # Convert first name to title case
            processed_data = convert_first_name_in_title_case(processed_data)
            st.write("Processed Data with First Name in Title Case:")
            st.write(processed_data.head())

if __name__ == "__main__":
    main()
