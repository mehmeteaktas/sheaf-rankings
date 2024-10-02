
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


#Put the File Path for the XML Dataset you want here. It should be the Posts.xml file of the Stack Exchange Dataset
df = pd.read_xml('Posts.xml', xpath='.//row', parser='etree')

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
df["Tags"] = df["Tags"].map(lambda x: x.strip('|').split('|') if x else [])
#Older datasets have different structures, thus this line is commented out for that reason
#df["Tags"] = df["Tags"].map(lambda x: x.strip('<>').split('><') if x else [])
df["OwnerUserId"] = df["OwnerUserId"].fillna(-3.0)

original_id_to_user = original_posts.set_index('Id')['OwnerUserId'].to_dict()

df["originalid"] = df["ParentId"].fillna(df["Id"])
df7 = df.groupby("originalid").agg({"OwnerUserId": list, "Tags": "first", "Id": list}).reset_index()
df7['OriginalPosterUserId'] = df7['originalid'].map(original_id_to_user)

df7_first_100 = df7
print(df7_first_100)

relevant_user_ids = set([user_id for sublist in df7_first_100["Id"] for user_id in sublist])
df_relevant = df[df["Id"].isin(relevant_user_ids)]


df3 = df_relevant.explode('Tags')[["OwnerUserId", "Score", "Tags"]]
df4_relevant = df3.groupby(["OwnerUserId", "Tags"])["Score"].sum().reset_index()
exploded_df = df7_first_100['Tags'].explode()
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
print(df7_first_100)

new_df = pd.DataFrame(columns=['UserID', 'Tag', 'InfectiveScore'])

#Switch this tag for whatever tag you want to check posts for
unique_tags_list = ["human-biology"]
for tag in unique_tags_list:


    df_tag = df7_first_100[df7_first_100['Tags'].apply(lambda tags: tag in tags)]
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
        start_time = time.time()

        print("shape", laplacian.shape)
        laplacian_energy = np.sum(linalg.eigvals(laplacian).real**2)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        for index, user in enumerate(list_of_users):
            new_mat = copy.deepcopy(laplacian)
            new_mat = np.delete(new_mat, index, 1)
            new_mat = np.delete(new_mat, index, 0)
            new_energy = np.sum(linalg.eigvals(new_mat).real**2)
            centrality = (laplacian_energy - new_energy)/laplacian_energy
            int_dict = main_dictionary.get(user, {})
            int_dict[tag] = centrality
            main_dictionary[user] = int_dict



data = []
for user, tags in main_dictionary.items():
    for tag, centrality in tags.items():
        data.append((user, tag, centrality))

df = pd.DataFrame(data, columns=['UserID', 'Tag', 'Centrality'])
df_sorted = df.sort_values(by=['Tag', 'Centrality'], ascending=[True, False])


#Change file name is whatever you want
df_sorted.to_csv('Non_sheaf_Hypergraph_laplacian_human_biology.csv', index=False)
print("DataFrame created and exported successfully!")

print(main_dictionary)

