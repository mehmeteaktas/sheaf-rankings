
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
from HyperRD.Hrandom import *
from HyperRD.Halgorithm import *
from HyperRD.Hgraph import *
from HyperRD.Hdynamic import *
from HyperRD.Htranslate import *
from HyperRD.Hmetric import *
import hypernetx as hnx
import random
import matplotlib.pyplot as plt
import time
#For this file to run properly you need to have the HyperRD Library downloaded in the project folder with this python file

# Load the data
df = pd.read_xml('/Posts.xml', xpath='.//row', parser='etree')

parent_tags = df.set_index('Id')['Tags'].to_dict()

original_posts = df[df['ParentId'].isna()]


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
#df["Tags"] = df["Tags"].map(lambda x: x.strip('<>').split('><') if x else [])
df["OwnerUserId"] = df["OwnerUserId"].fillna(-3.0)

original_id_to_user = original_posts.set_index('Id')['OwnerUserId'].to_dict()

# Create df7: OriginalId and list of OwnerUserIds
df["originalid"] = df["ParentId"].fillna(df["Id"])
df7 = df.groupby("originalid").agg({"OwnerUserId": list, "Tags": "first", "Id": list}).reset_index()
df7['OriginalPosterUserId'] = df7['originalid'].map(original_id_to_user)

# Get the first 100 rows of df7
filtered_df = df7
print(filtered_df)

relevant_user_ids = set([user_id for sublist in filtered_df["Id"] for user_id in sublist])
df_relevant = df[df["Id"].isin(relevant_user_ids)]


# Create df4: UserId, Score, and Tags
df3 = df_relevant.explode('Tags')[["OwnerUserId", "Score", "Tags"]]
df4_relevant = df3.groupby(["OwnerUserId", "Tags"])["Score"].sum().reset_index()
# Get relevant user IDs from filtered_df
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

tag = "human-biology"

#Change this to whatever tag you want to explore
unique_tags_list = ['human-biology']
for tag in unique_tags_list:

    print(tag)
    df_tag = filtered_df[filtered_df['Tags'].apply(lambda tags: tag in tags)]
    print(df_tag)
    print(unique_tags_list)



    def compute_mutual_information(trajectory1, trajectory2, bins=10):
        # Compute histograms
        hist_1, _ = np.histogram(trajectory1, bins=bins, density=True)
        hist_2, _ = np.histogram(trajectory2, bins=bins, density=True)
        
        # Compute joint histogram
        joint_hist, _, _ = np.histogram2d(trajectory1, trajectory2, bins=bins, density=True)
        
        # Compute mutual information
        eps = np.finfo(float).eps
        mutual_info = np.sum(joint_hist * np.log2((joint_hist + eps) / (np.outer(hist_1, hist_2) + eps)))
        
        return mutual_info

 
    
    infection_probability = 0.15
    recovery_probability = 1

 
    graph = Create()
    for index, row in df_tag.iterrows():

        print(row["OwnerUserId"])
        graph.add_edge(row["OwnerUserId"])
    num_vertices = len(graph.vertices)
    vertices = list(graph.vertices)
    print(graph.vertices)
    print("tag", tag)
    total_weight = 0
    print(userdict)
    counter = 0
    for users in userdict:
        print(users)
        if userdict[users].get(tag, "howdy") != "howdy":
            counter += 1
            total_weight += userdict[users][tag]
    average_weight = total_weight/counter

    average_degree = average_vertex_degree(graph)*(average_edge_size(graph) - 1)*average_weight
    print("average degree", average_degree)
    print("tag", tag)
    infection_rate = (average_degree)/((average_degree)**2 - (average_degree))
    
    print("infection_rate", infection_rate)
  
    infection_probability = infection_rate
    # Initialize states
    num_steps = 50
    states = {}  # S: Susceptible, I: Infected, R: Recovered
    for z in graph.vertices:
        runninglist = []
        start_time = time.time()  # Start timing

        for m in range(50):
            initial_infected = z
            for v in vertices:
                states[v] = "S"
            states[z] = "I"

                
            # Lists to store the trajectory
            susceptible_traj = [len([v for v in states.values() if v == 'S'])]
            infected_traj = [len([v for v in states.values() if v == 'I'])]
            recovered_traj = [len([v for v in states.values() if v == 'R'])]
            #print("vertices", vertices)

            # Simulation function
            def simulate_step():
                new_states = states.copy()
                for e in graph.edges:
                #  print([v for v in e])
                    infected = [v for v in e if states.get(v, "S") == 'I']
                    int_list = []
                    for v in e:
                        int_list.append(userdict[v][tag])
                    meann = np.mean(int_list)
                    local_infection_probability = infection_probability
                    local_infection_probability = (1 - (1- infection_probability)**meann)
                    #print(local_infection_probability, "Local infection probability")
                    #print("Local Infection", local_infection_probability)
                    if infected:
                        for v in e:
                            if states.get(v, "S") == 'S' and random.random() < 1 - (1 - local_infection_probability)**len(infected):
                                new_states[v] = 'I'
                            elif states.get(v, "S") == 'I' and random.random() < recovery_probability:
                                new_states[v] = 'R'
                return new_states



            # Run the simulation
            for step in range(num_steps):
                states = simulate_step()
                susceptible_traj.append(len([v for v in states.values() if v == 'S']))
                infected_traj.append(len([v for v in states.values() if v == 'I']))
                recovered_traj.append(len([v for v in states.values() if v == 'R']))
            end_time = time.time()  # End timing

            runninglist.append(recovered_traj[-1] + infected_traj[-1])
        elapsed_time = end_time - start_time
            #print(recovered_traj[-1] + infected_traj[-1])
        print(f"Elapsed time: {elapsed_time} seconds")
        print(np.mean(runninglist))
        new_df.loc[len(new_df)] = [z, tag, np.mean(runninglist)]

 

new_df.to_csv('Hypergraph_Biology_SIR.csv', index=False)