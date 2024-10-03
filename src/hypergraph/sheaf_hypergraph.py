
import pandas as pd
import copy
from collections import defaultdict
import numpy as np
import scipy
from scipy import sparse
from scipy import linalg
from scipy.sparse.linalg import eigs
from scipy.linalg import issymmetric

import time


# Load the data, should be the posts.xml file of a stack exchange dataset
df = pd.read_xml('tempdata', xpath='.//row', parser='etree')

parent_tags = df.set_index('Id')['Tags'].to_dict()


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


# Create df7: OriginalId and list of OwnerUserIds
df["originalid"] = df["ParentId"].fillna(df["Id"])
df7 = df.groupby("originalid").agg({"OwnerUserId": list, "Tags": "first", "Id": list}).reset_index()

# Get the first 100 rows of df7
df7_first_100 = df7
df7_first_100
tag = "machine-learning"
df7_first_100 = df7_first_100[df7_first_100['Tags'].apply(lambda tags: tag in tags)]

relevant_user_ids = set([user_id for sublist in df7_first_100["Id"] for user_id in sublist])
df_relevant = df[df["Id"].isin(relevant_user_ids)]

# Create df4: UserId, Score, and Tags
df3 = df_relevant.explode('Tags')[["OwnerUserId", "Score", "Tags"]]
df4_relevant = df3.groupby(["OwnerUserId", "Tags"])["Score"].sum().reset_index()
# Get relevant user IDs from df7_first_100

# Filter df4 to include only relevant user IDs
#df4_relevant = df4[df4["OwnerUserId"].isin(relevant_user_ids)]

# Display the resulting DataFrames
print("First 100 rows of df7:")
print(df7_first_100)

print("Filtered df4 with relevant user IDs:")
print(df4_relevant.head(20))


#Userdict is a dictionary with key being user id, and value being a dictionary
#The inner dictionary has key of tag, and value of score
num_users = 0
num_tags = 0
userdict = {}
tagdict ={}
for user in df4_relevant["OwnerUserId"].unique():
    num_users += 1
    tagdict ={}
    df_user = df4_relevant[df4_relevant["OwnerUserId"] == user]
    for tag in df_user["Tags"]:
        tagdict[tag] = df_user[df_user["Tags"] == tag]["Score"].values[0]
    userdict[user] = tagdict

num_keys = len(userdict)
print("num_users = ", num_users)
print("num_tags = ", num_tags)
print(num_keys)
# Calculate the average number of tags
df_exploded = df7_first_100.explode('OwnerUserId')

# Group by 'OwnerUserId' and collect the associated 'originalid's into a list
grouped_data = df_exploded.groupby('OwnerUserId')['originalid'].agg(list)

# Convert the grouped data into a dictionary
owner_to_originalid_dict = grouped_data.to_dict()


Post_Tags_Dict = df7_first_100.set_index('originalid')['Tags'].to_dict()

#Userdict but will for each post have a different dictionary will all non active tags set to zero
active_tag_dictionary = {}
for user in df4_relevant["OwnerUserId"]:
    smalldict = {}
    for post in owner_to_originalid_dict[user]:
        dictcopy = copy.deepcopy(userdict[user])
        for key in dictcopy.keys():
            if key not in Post_Tags_Dict[post]:
                dictcopy[key] = 0
        smalldict[post] = dictcopy
    active_tag_dictionary[user] = smalldict



runningsum = 0
#Dictionary has userid as key, and the value is when in the laplacian matrix the user begins
user_start_index = {}
for user in userdict:
    user_start_index[user] = runningsum
    runningsum += len(userdict[user])

laplacian = sparse.lil_matrix((runningsum, runningsum))
print(runningsum)

degreedict = {}
#The key for the following dictionary is a tuple of two user ids, and the value is the posts that they share
edges_for_two_nodes = defaultdict(list)
for index, row in df7_first_100.iterrows():
    users = row["OwnerUserId"]
    users = [user for user in users if not (pd.isna(user) or user is None)]
    degreedict[row['originalid']] = len(users)
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            pair = tuple(sorted([users[i], users[j]]))
            edges_for_two_nodes[pair].append(row['originalid'])

edges_for_two_nodes = dict(edges_for_two_nodes)

#print(edges_for_two_nodes)
#print(degreedict)


def laplacian_matrix(id1, id2, postid, degreedict, arraydict):
    list1 = list(arraydict[id1][postid].values())
    list2 = list(arraydict[id2][postid].values())
    array1 = np.array(list1).reshape(1, -1)
    array2 = np.array(list2).reshape(1, -1)
    return (1/degreedict[postid])*np.matmul(array1.transpose(), array2)


def insert_into_sparse(dense, sparse, entryrow, entrycol):
    rows = dense.shape[0]
    cols = dense.shape[1]
    sparse[entryrow:entryrow+rows, entrycol:entrycol+cols] = dense
    return sparse


for pair in edges_for_two_nodes:
    v1 = pair[0]
    v2 = pair[1]
    startrow = user_start_index[v1]
    startcol = user_start_index[v2]
    runningsum = np.zeros([len(userdict[v1]), len(userdict[v2])])
    for post in edges_for_two_nodes[pair]:
        runningsum = runningsum + laplacian_matrix(v1, v2, post, degreedict, active_tag_dictionary)
    runningsum = -1 * runningsum
   # print(runningsum)
    laplacian = insert_into_sparse(runningsum, laplacian, startrow, startcol)
    v1 = pair[1]
    v2 = pair[0]
    startrow = user_start_index[v1]
    startcol = user_start_index[v2]
    runningsum = np.zeros([len(userdict[v1]), len(userdict[v2])])
    for post in edges_for_two_nodes[pair]:
        runningsum = runningsum + laplacian_matrix(v1, v2, post, degreedict, active_tag_dictionary)
    runningsum = -1 * runningsum
    laplacian = insert_into_sparse(runningsum, laplacian, startrow, startcol)

check = 0
for user in userdict:
    check += 1
    runningsum = np.zeros([len(userdict[user]), len(userdict[user])])
    startrow = user_start_index[user]
    startcol = user_start_index[user]
    for post in active_tag_dictionary[user]:
        runningsum = runningsum + laplacian_matrix(user, user, post, degreedict, active_tag_dictionary)
    laplacian = insert_into_sparse(runningsum, laplacian, startrow, startcol)


laplacian = laplacian.todense()
start_time = time.time()

dense_eigens = linalg.eigvals(laplacian)
dense_eigens = dense_eigens.real
end_time = time.time()
elapsed_time = end_time - start_time
original_energy = np.sum(dense_eigens**2)
maxval = 0
minvalue = 0
energy_dict = copy.deepcopy(userdict)
for user in energy_dict:
    for i, tag in enumerate(energy_dict[user]):
      #  if tag == "machine-learning":
        int_mat = np.copy(laplacian)
        int_mat = np.delete(int_mat, user_start_index[user] + i, 1)
        int_mat = np.delete(int_mat, user_start_index[user] + i, 0)
        eigens = linalg.eigvals(int_mat)
        eigens = eigens.real
        centrality = (original_energy - np.sum(eigens**2))/original_energy
        if centrality > maxval:
            maxval = centrality
        if centrality < minvalue:
            minvalue = centrality
        energy_dict[user][tag] = centrality


tagdict = {}
for user in energy_dict:
    for tag in energy_dict[user]:
        if abs(tagdict.get(tag, (0, 0))[1]) < abs(energy_dict[user][tag]):
            tagdict[tag] = (user, energy_dict[user][tag])

data = []
for user, tags in energy_dict.items():
    for tag, centrality in tags.items():
        data.append((user, tag, centrality))

# Create a DataFrame
df = pd.DataFrame(data, columns=['UserID', 'Tag', 'Centrality'])
df = df[df["Tag"] == "machine-learning"]
df_sorted = df.sort_values(by=['Tag', 'Centrality'], ascending=[True, False])

#Change Filename to whatever you need it to be
df_sorted.to_csv('onlyml_sheafcentrality_data_350.csv', index=False)
print("DataFrame created and exported successfully!")
