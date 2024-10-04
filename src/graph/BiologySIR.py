#!/usr/bin/env python
# coding: utf-8

# In[12]:


import EoN
import matplotlib.pyplot as plt


# In[13]:


import numpy as np
import pandas as pd


# In[14]:


df = pd.read_xml('BiologyPosts.xml', xpath='.//row', parser= 'etree')
df['Question'] = False
for index, row in df.iterrows():
    if pd.isna(row['ParentId']):
        df.at[index,'ParentId'] = row['Id']
        df.at[index,'Question'] = True
    else:
         df.at[index, 'Tags'] = df.loc[df['Id']==row['ParentId'], 'Tags'].iloc[0]


df["Tags"] = df["Tags"].map(lambda x: x.strip('|').split('|') if x else [])

df_exploded = df.explode('Tags')

df_cleaned = df_exploded.dropna(subset=['OwnerUserId'])

#print(df_cleaned['Tags'].nunique())

grouped_df = df_cleaned.groupby(['OwnerUserId', 'Tags'])['Score'].sum().reset_index()
grouped_df.head(20)


# In[15]:


tag_itself = [0] * (df_exploded['Tags'].nunique()+1)
by_tag = [0] * (df_exploded['Tags'].nunique()+1)

big_count = 0

for index,row in df_exploded.iterrows():
    if row['Tags'] not in tag_itself:
        if not pd.isna(df.at[index,'OwnerUserId']):
            tag_itself[big_count] = row['Tags']
            by_tag[big_count] = list()
            by_tag[big_count].append(row['ParentId'])
            big_count += 1
    else:
        if not pd.isna(df.at[index,'OwnerUserId']):
            if row['ParentId'] not in by_tag[tag_itself.index(row['Tags'])]:
                by_tag[tag_itself.index(row['Tags'])].append(row['ParentId'])


# In[16]:


post_grouping = [0] * df['ParentId'].nunique() 
big_count = 0
poster_grouping = [0] * df['ParentId'].nunique()

for index,row in df.iterrows():
    if row['ParentId'] not in poster_grouping:
        if not pd.isna(df.at[index,'OwnerUserId']):
            poster_grouping[big_count] = row['ParentId']
            post_grouping[big_count] = list()
            post_grouping[big_count].append((row['OwnerUserId'],row['Question']))
            big_count += 1
        else:
            ("")
    elif row['ParentId'] in poster_grouping:
        if not pd.isna(df.at[index,'OwnerUserId']):
            post_grouping[poster_grouping.index(row['ParentId'])].append((row['OwnerUserId'],row['Question']))
        else:
            ("")
#print(post_grouping)


# In[17]:


import networkx as nx
def adding_edges(post_grouping, poster_grouping, tag_itself, by_tag):
    graphs = dict()
    question = None
    for tag in tag_itself:
        if tag == "human-biology":
            print(1)
            graphs[tag] = nx.Graph()
            for i in range(len(post_grouping)):
                if isinstance(post_grouping[i], list):
                    if (poster_grouping[i] in by_tag[tag_itself.index(tag)]):
                        for tup in post_grouping[i]:
                            small_count = len(post_grouping[i]) - 1
                            while small_count > (post_grouping[i].index(tup)-1):
                                if not graphs[tag].has_node(tup[0]):
                                    graphs[tag].add_node(tup[0])
                                if not graphs[tag].has_node(post_grouping[i][small_count]):
                                    graphs[tag].add_node(post_grouping[i][small_count][0])
                                if not graphs[tag].has_edge(tup[0], post_grouping[i][small_count][0]):
                                    graphs[tag].add_edge(tup[0], post_grouping[i][small_count][0])
                                small_count -= 1
                    else:
                        ("")
    return graphs

graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)
import matplotlib.pyplot as plt
pos = nx.spring_layout(graphs['human-biology'])
nx.draw(graphs['human-biology'], pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=15)

print(len(graphs['human-biology']))
# In[18]:


def running_sir(graphs, tag_itself):
    stuff = [0]
    stuff[0] = list()
    for tag in tag_itself:
        if tag == "human-biology":
            if (len(graphs[tag]) > 1):
                mu = len(graphs[tag].nodes())/(((len(graphs[tag].nodes())**2)-len(graphs[tag].nodes())))
            else:
                mu = 2/2
            infection_rates = {node: (1-(1-mu)**(grouped_df.loc[(grouped_df['OwnerUserId']==node) & (grouped_df['Tags']==tag), 'Score'].iloc[0])) for node in graphs[tag].nodes()}
            for node in graphs[tag].nodes():
                gamma = 1
                state = {node: 0 for node in graphs[tag].nodes()}
                state[node] = 1
                timesteps = 50
                counter = 0
                summing = 0
                while counter < 50:
                    for t in range(timesteps):
                        new_state = state.copy()
                        for k in graphs[tag].nodes():
                            if state[k] == 1:
                                for neighbor in graphs[tag].neighbors(k):
                                    if state[neighbor] == 0:
                                        if np.random.rand() < infection_rates[k]:
                                            new_state[neighbor] = 1
                                if np.random.rand() < gamma:
                                    new_state[k] = 2
                        state = new_state
                    summing += sum(1 for k in state if (state[k] == 1 or state[k] == 2))
                    state = {node: 0 for node in graphs[tag].nodes()}
                    state[node] = 1
                    counter += 1
            
                stuff[0].append({node : summing/50})

    return stuff
        
stuff = running_sir(graphs, tag_itself)
print(len(stuff[0]))

        


# In[19]:


new_list = list()
for i in stuff:
    sorted_items = sorted(i, key=lambda d: list(d.values())[0], reverse=True)
    new_list.append(sorted_items)


# In[20]:


new_list
print(len(new_list[0]))


# In[21]:


newer_list = list()
for i in new_list:
    tuple_list = [(key, value) for d in i for key, value in d.items()]
    newer_list.append(tuple_list)
print(len(newer_list[0]))

# In[22]:


newer_list


# In[24]:


arr = []
users = [x[0] for x in newer_list[0]]
arr.append({'human-biology': users})
arr


# In[25]:


flattened_data = []
index = 1
for d in arr:
    for key,value in d.items():
        if isinstance(value, list):
            for item in value:
                flattened_data.append((key,item,index))
                index += 1
        else:
            flattened_data.append((key,item))
        index = 1
flattened_data
print(len(flattened_data))


# In[80]:


df = pd.DataFrame(flattened_data, columns=['Tag', 'OwnerUserId', 'Rank'])

# Save to CSV
df.to_csv('BiologySIRrankOutput.csv', index=False)

print("CSV file created successfully.")


# In[ ]:




