
import pandas as pd
import copy
from collections import defaultdict
import numpy as np
import scipy
from scipy import sparse
from scipy import linalg
from scipy.sparse.linalg import eigs
from scipy.linalg import issymmetric
from numpy.linalg import inv
from numpy import linalg as LA
import hypernetx as hnx
import networkx as nx
import random
from hypernetx.algorithms import laplacians_clustering as lap
import matplotlib.pyplot as plt
import time

def is_connected(hypergraph):
    import networkx as nx
    G = hnx.Hypergraph.to_incidence_graph(hypergraph)
    return nx.is_connected(G)

def connected_components(hypergraph):
    import networkx as nx
    G = hnx.Hypergraph.to_incidence_graph(hypergraph)
    return nx.connected_components(G)
# Load the data

df = pd.read_xml('tempdata', xpath='.//row', parser='etree')

parent_tags = df.set_index('Id')['Tags'].to_dict()

original_posts = df[df['ParentId'].isna()]
main_dictionary = {}

# Function to inherit tags from parent posts
def inherit_tags(row):
    if pd.isna(row['Tags']) and row['ParentId'] in parent_tags:
        return parent_tags[row['ParentId']]
    return row['Tags']

# Apply the function to the dataframe
df['Tags'] = df.apply(inherit_tags, axis=1)

# Replace NaN with None
df = df.where(pd.notnull(df), None)
# Process the Tags column
#df["Tags"] = df["Tags"].map(lambda x: x.strip('|').split('|') if x else [])
df["Tags"] = df["Tags"].map(lambda x: x.strip('<>').split('><') if x else [])
df["OwnerUserId"] = df["OwnerUserId"].fillna(-3.0)

original_id_to_user = original_posts.set_index('Id')['OwnerUserId'].to_dict()

# Create df7: OriginalId and list of OwnerUserIds
df["originalid"] = df["ParentId"].fillna(df["Id"])
df7 = df.groupby("originalid").agg({"OwnerUserId": list, "Tags": "first", "Id": list}).reset_index()
df7['OriginalPosterUserId'] = df7['originalid'].map(original_id_to_user)

filtered_df = df7
print(filtered_df)

relevant_user_ids = set([user_id for sublist in filtered_df["Id"] for user_id in sublist])
df_relevant = df[df["Id"].isin(relevant_user_ids)]


# Create df4: UserId, Score, and Tags
df3 = df_relevant.explode('Tags')[["OwnerUserId", "Score", "Tags"]]
df4_relevant = df3.groupby(["OwnerUserId", "Tags"])["Score"].sum().reset_index()
# Get relevant user IDs from df7
exploded_df = filtered_df['Tags'].explode()
cleaned_df = exploded_df.dropna()

unique_tags = cleaned_df.unique()
unique_tags_list = unique_tags.tolist()

num_users = 0
num_tags = 0
userdict = {}
tagdict ={}
for user in df4_relevant["OwnerUserId"].unique():
    tagdict ={}
    df_user = df4_relevant[df4_relevant["OwnerUserId"] == user]
    for tag in df_user["Tags"]:
        tagdict[tag] = df_user[df_user["Tags"] == tag]["Score"].values[0]
    userdict[user] = tagdict

num_keys = len(userdict)
print("num_users = ", num_users)
print("num_tags = ", num_tags)
print(num_keys)

print(df_relevant)
print(filtered_df)

new_df = pd.DataFrame(columns=['UserID', 'Tag', 'InfectiveScore'])


#Change to whatever tag you want to do
tag = "machine-learning"
unique_tags_list = ["machine-learning"]
for tag in unique_tags_list:


    df_tag = filtered_df[filtered_df['Tags'].apply(lambda tags: tag in tags)]
    lengths = df_tag['OwnerUserId'].apply(len)

    unique_lengths = list(set(lengths))
    df_tag["lengths"] = df_tag['OwnerUserId'].apply(len)
    list_of_users = (df_tag['OwnerUserId'].explode()).unique()
    list_of_users = sorted(list_of_users)
    print(list_of_users)
    num_cols = len(list_of_users)
    if len(list_of_users) < 2:
        int_dict = main_dictionary.get(user, {})
        int_dict[tag] = 0
        main_dictionary[user] = int_dict
    
    else:
        list_of_rows = []
        matrix_dictionary = {}
        print(tag)
        for length in unique_lengths:
            list_of_rows = []
            for index, rows in df_tag[df_tag["lengths"] == length].iterrows():
                row_one = np.zeros(num_cols)
                for i, user in enumerate(list_of_users):
                    if user in rows["OwnerUserId"]:
                        row_one[i] = 1
                list_of_rows.append(row_one)
            matrix_one = np.asarray(list_of_rows)
            matrix_dictionary[length] = copy.deepcopy(np.matmul(np.transpose(matrix_one), matrix_one))
        laplacian = np.zeros([num_cols, num_cols])
        for length in lengths:
            laplacian = laplacian + matrix_dictionary[length]
        for i in range(num_cols):
            laplacian[i, i] = 0
        graph = nx.from_numpy_array(laplacian)
        pagerank = nx.pagerank(graph)
        pg_dict = {}
        for i, user in enumerate(list_of_users):
            pg_dict[user] = pagerank[i]
        

       



# Create a DataFrame

df = pd.DataFrame(list(pg_dict.items()), columns=['UserID', 'PageRankValue'])

# Adding a Rank column based on the PageRankValue, with the highest value ranked as 1
df['Rank'] = df['PageRankValue'].rank(ascending=False, method='min').astype(int)

# Sorting the DataFrame by Rank
df = df.sort_values(by='Rank')

# Exporting to CSV
df.to_csv('pagerank_output.csv', index=False)

print("CSV file has been created successfully.")


