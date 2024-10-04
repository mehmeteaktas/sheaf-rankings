#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
df = pd.read_xml('ORPosts.xml', xpath='.//row', parser= 'etree')

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

print(df_cleaned['Tags'].nunique())

df_exploded.head(20)


# In[5]:


tag_itself = [0] * (df_exploded['Tags'].nunique()+1)
by_tag = [0] * (df_exploded['Tags'].nunique()+1)

big_count = 0

for index,row in df_exploded.iterrows():
    if row['Tags'] not in tag_itself:
        if not pd.isna(df.at[index,'OwnerUserId']):
            tag_itself[big_count] = row['Tags']
            print(tag_itself[big_count])
            by_tag[big_count] = list()
            by_tag[big_count].append(row['ParentId'])
            big_count += 1
    else:
        if not pd.isna(df.at[index,'OwnerUserId']):
            if row['ParentId'] not in by_tag[tag_itself.index(row['Tags'])]:
                by_tag[tag_itself.index(row['Tags'])].append(row['ParentId'])


# In[6]:


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
print(post_grouping)


# In[7]:


import networkx as nx
def adding_edges(post_grouping, poster_grouping, tag_itself, by_tag):
    graphs = dict()
    question = None
    for tag in tag_itself:
        if tag == "optimization":
            graphs[tag] = nx.Graph()
            for i in range(len(post_grouping)):
                if isinstance(post_grouping[i], list):
                    if (poster_grouping[i] in by_tag[tag_itself.index(tag)]):
                        for tup in post_grouping[i]:
                            small_count = len(post_grouping[i]) - 1
                            while small_count > post_grouping[i].index(tup):
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
pos = nx.spring_layout(graphs['optimization'])
nx.draw(graphs['optimization'], pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=15)


# In[ ]:

#doing Sheaf Laplacian
ordered_df = pd.read_csv('or.csv')
count = 0
total_sum = 0
initial_sum = 0
for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['optimization']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    if (count == 0):
        initial_sum = sum
    total_sum += (sum/initial_sum)
    count = count + 1
    if (graphs['optimization'].has_node(row['Owner'])):
        graphs['optimization'].remove_node(row['Owner'])
sheaf_average = (total_sum/(count))

# In[ ]:
#doing NonSheaf Laplacian
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('OperationsReasearchNonSheafLaplacian.csv') #change
total_sum = 0
initial_sum = 0
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['optimization']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    if (count == 0):
        initial_sum = sum
    total_sum += (sum/initial_sum)
    count = count + 1
    if (graphs['optimization'].has_node(row['Owner'])):
        graphs['optimization'].remove_node(row['Owner'])
laplacian_average = (total_sum/(count))


# In[ ]:
#doing SIR
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('OperationsSIROutput.csv') #change
total_sum = 0
initial_sum = 0
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['optimization']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    if (count == 0):
        initial_sum = sum
    total_sum += (sum/initial_sum)
    count = count + 1
    if (graphs['optimization'].has_node(row['OwnerUserId'])):
        graphs['optimization'].remove_node(row['OwnerUserId'])
sir_average = (total_sum/(count))

#doing page rank
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('OperationsPageRankoutput.csv') #change
total_sum = 0
initial_sum = 0
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['optimization']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    if (count == 0):
        initial_sum = sum
    total_sum += (sum/initial_sum)
    count = count + 1
    if (graphs['optimization'].has_node(row['OwnerUserId'])):
        graphs['optimization'].remove_node(row['OwnerUserId'])
page_average = (total_sum/(count))


#doing reputation
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('reputation_optimization.csv') #change
total_sum = 0
initial_sum = 0
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['optimization']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    if (count == 0):
        initial_sum = sum
    total_sum += (sum/initial_sum)
    count = count + 1
    if (graphs['optimization'].has_node(row['UserId'])):
        graphs['optimization'].remove_node(row['UserId'])
reputation_average = (total_sum/(count))

# In[ ]:


import matplotlib.pyplot as plt
plt.figure(figsize=(8,6))
values = [sheaf_average, laplacian_average, sir_average, page_average, reputation_average]
categories = ['Sheaf Laplacian', 'Non-Sheaf Laplacian', 'SIR', 'Page Rank', 'Reputation']
plt.bar(categories, values, color='orange')

plt.tight_layout()
plt.title('graph operations research')
plt.savefig('OperationsAreaUnderCurve.png')

