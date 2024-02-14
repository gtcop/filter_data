import pandas as pd 
import streamlit as st
# function to convert the data of the file into the lower case

def email_approch():
    def convert_into_lowercase(input_file):
        df = pd.read_csv(input_file)                        #input file 
        df.columns = df.columns.str.lower()                 # Convert column names to lowercase
        df = df.apply(lambda x: x.astype(str).str.lower())  # Convert all data to lowercase
        return df

    # function to arrange single email address in as single row
    def email_list(output_file2):
        df = output_file2   # Read the CSV file into a DataFrame
        def extract_emails(row): # Define a function to split and extract emails
            emails = row.split() # Split by space
            return emails

        df['list_of_emails'] = df['email'].apply(extract_emails)  # Apply the function to create a new column with lists of emails
        exploded_df = df.explode('list_of_emails')                 # Explode the lists into separate rows
        exploded_df = exploded_df.drop('email', axis=1).reset_index(drop=True)   # Drop the original column and reset the index
        return exploded_df

    # function to extract the domains from the email address
    def extract_email_domain(email):
        if pd.notna(email) and "@" in email:
            return email.split("@")[1]
        return ""

    # function to compare the domains of email from 2 files and print matched whereever found
    def process_file(output_file1, exploded_df):
        df_s1 = output_file1   # Read the first CSV file
        df1 = exploded_df   # Read the second CSV file
        df_s1['status'] = 'na'              # Create new columns 'status', 'reason', 'match_condition', and 'original_index'
        df_s1['reason'] = 'na'
        df_s1['match_condition'] = 'na'
        df_s1['original_index'] = df_s1.index  # Create a new column to store original indices

        for i in range(len(df_s1)):            # Iterate through the indices of the two DataFrames
            match_found = False
            matching_reason = 'na'
            match_condition = 'na'

            domain_df_s1 = extract_email_domain(df_s1['email'].iloc[i])

            if any(domain_df_s1 == extract_email_domain(df1.iloc[j]['list_of_emails']) for j in range(len(df1))):  # Check for exact domain match
                df_s1.at[i, 'status'] = 'matched'
                match_found = True
                match_condition = 'email_domain_match'
                matching_reason = domain_df_s1

            if match_found:
                df_s1.at[i, 'reason'] = matching_reason
                df_s1.at[i, 'match_condition'] = match_condition

        # Sort the DataFrame based on the original indices
        df_output = df_s1.sort_values(by='original_index').reset_index(drop=True)
        return df_output  # Save the modified DataFrame to a new CSV file


    # funtion to extract the matched results and unmatched results for further processing
    def seperate_matched_and_unmatched(df_output):
        df = df_output
        un_matched = df[df['status'] != 'matched']  # Drop rows where the 'email_column' is empty or NaN and 'status' column is "matched or na "
        matched = df[df['status'] != 'na']          # Drop rows where the 'email_column' is empty or NaN and 'status' column is na "
        print(un_matched)
        print(matched)
        return un_matched, matched

    # funtion to process the file processing part 2 
    def file_processing_step_2(un_matched, output_file3):
        df1 = un_matched.copy()
        df2 = output_file3
        df1['status'] = 'na'  # Create a new 'status' column and initialize it with 'na'

        for index, row in df1.iterrows():     # Iterate through each row in df1 and check for matches in df2
            email_to_match = row['email']
            if email_to_match in df2['email'].values:   # Check if the email_to_match is present in df2
                df1.at[index, 'status'] = 'matched'
        return df1

    # convert first letter of first name into upper case
    def first_name_in_upper_case(df1):
        df = df1.copy()
        col = "first name"
        df[col] = df[col].apply(lambda x: x.title())     # Capitalize the first letter of each word in the 'Column1' column
        return df

    # Streamlit app
    def main():
        st.title("Filter file by company email domain")
        # Sidebar for file uploads
        st.sidebar.header("Upload Files")
        f1 = st.sidebar.file_uploader("Upload file 1 (campaign_data.csv)", type="csv")
        f2 = st.sidebar.file_uploader("Upload file 2 (all_clients_data.csv)", type="csv")
        additional_file_option = st.sidebar.radio("Do you have an additional file to check?", ('Yes', 'No'))

        if f1 and f2:
            a1 = "raw_data"
            a2 = "client_email_domain_list"
            a3 = "campaign_used_list"
            output_file1 = convert_into_lowercase(f1)
            st.header(a1)
            st.write(output_file1)
            output_file2 = convert_into_lowercase(f2)
            st.write(a2)
            st.write(output_file2)

            if additional_file_option == 'Yes':
                f3 = st.sidebar.file_uploader("Upload file 3 (any_optional_data.csv)", type="csv")
                if f3:
                    output_file3 = convert_into_lowercase(f3)
                    st.header(a3)
                    st.write(output_file3)
                    exploded_df = email_list(output_file2)
                    st.header(f"retrieved email from {a2} data file and arranged in rows")
                    st.write(exploded_df)
                    df_output = process_file(output_file1, exploded_df)
                    st.header(f"data compared from {a1} and {a2} data file and appended matched or unmatched where the condition matched")
                    st.write(df_output)
                    un_matched, matched = seperate_matched_and_unmatched(df_output)
                    df1 = file_processing_step_2(un_matched, output_file3)
                    st.header(f"data filtered from {a3} data file and output of {a1} and {a2} data file")
                    st.write(df1)
                    df = first_name_in_upper_case(df1)
                    st.header(f"final output file after all processing ready to launch campaign")
                    st.write(df)
                else:
                    st.sidebar.warning("Please upload the additional file to continue.")

            elif additional_file_option == 'No':
                exploded_df = email_list(output_file2)
                st.header(f"retrieved email from {a2} data file and arranged in rows")
                st.write(exploded_df)
                df_output = process_file(output_file1, exploded_df)
                st.header(f"data compared from {a1} and {a2} data file and appended matched or unmatched where the condition matched")
                st.write(df_output)
                un_matched, matched = seperate_matched_and_unmatched(df_output)
                st.header(f"Unmatched data from {a1}")
                st.write(un_matched)
                st.header(f"Matched data from {a1}")
                st.write(matched)

    if __name__ == "__main__":
        main()


def company_name_approch():

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
        # usefull_cols = ["company name", "first name", "email", "status","reason","match_reason"]
        # df_s1 = df_s1[usefull_cols]
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
