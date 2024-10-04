#!/usr/bin/env python
# coding: utf-8

# In[5]:


import numpy as np
import pandas as pd

df = pd.read_xml('AstronomyPosts.xml', xpath='.//row', parser= 'etree')
df['Question'] = False
for index, row in df.iterrows():
    if pd.isna(row['ParentId']):
        df.at[index,'ParentId'] = row['Id']
        df.at[index,'Question'] = True
    else:
         df.at[index, 'Tags'] = df.loc[df['Id']==row['ParentId'], 'Tags'].iloc[0]


df["Tags"] = df["Tags"].map(lambda x: x.strip('|').split('|') if x else [])

df_exploded = df.explode('Tags')


# In[6]:

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

# In[7]:


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


# In[8]:


import networkx as nx


# In[9]:


import networkx as nx
def adding_edges(post_grouping, poster_grouping, tag_itself, by_tag):
    graphs = dict()
    question = None
    for tag in tag_itself:
        if tag == "observational-astronomy":
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
pos = nx.spring_layout(graphs['observational-astronomy'])
nx.draw(graphs['observational-astronomy'], pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=15)


# In[10]:


adjacency_matrix = nx.adjacency_matrix(graphs['observational-astronomy']).todense()
#print(adjacency_matrix)


# In[11]:


degrees = [val for (node, val) in graphs['observational-astronomy'].degree()]
names_arr = [0] * len(graphs['observational-astronomy'])
counter = 0
for node in graphs['observational-astronomy'].nodes():
    names_arr[counter] = node
    counter += 1  
diagonal_matrix = np.diag(degrees)
print(len(names_arr))
#print(diagonal_matrix)


# In[12]:


Laplacian = diagonal_matrix - adjacency_matrix


# In[13]:


#print(Laplacian)


# In[14]:


eigenvalues, eigenvectors = np.linalg.eig(Laplacian)
eigenvalues


# In[15]:


eigenvalues = eigenvalues.real


# In[16]:


eigenvalues
sum_laplace = 0
for i in range(len(eigenvalues)):
    sum_laplace += (eigenvalues[i]**2)
sum_laplace


# In[ ]:


centrality = []
for i in range(len(names_arr)):
    modified_matrix = np.delete(Laplacian, i, axis=1)
    modified_matrix = np.delete(modified_matrix, i, axis=0)
    eigenvalues, eigenvectors = np.linalg.eig(modified_matrix)
    eigenvalues = eigenvalues.real
    summer_laplace = 0
    for i in range(len(eigenvalues)):
        summer_laplace += (eigenvalues[i]**2)
    centrality.append(summer_laplace)
centrality
print(len(centrality))


# In[ ]:


def calculate_centralities(sum_laplace, centrality):
    centralities = []
    for i in centrality:
        score = (sum_laplace-i)/(sum_laplace)
        centralities.append(score)
    return centralities

centralities = calculate_centralities(sum_laplace, centrality)


# In[ ]:


def tupify(names_arr, centralities):
    arr = []
    count = 0
    for i in range(len(names_arr)):
        arr.append((names_arr[i],centralities[i]))
    return arr
scorings = tupify(names_arr, centralities)


# In[ ]:


import csv

with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(scorings)
final_df = pd.read_csv('output.csv',header=None)
final_df.columns = ['Owner','Centrality']
final_df


# In[ ]:


final_df['Rank'] = final_df['Centrality'].rank(method='dense', ascending=False)
final_df = final_df.sort_values(by='Rank')
final_df = final_df.reset_index(drop=True)
final_df.head(20)

# Save to CSV
final_df.to_csv('NonSheafLaplacian.csv', index=False)

print("CSV file created successfully.")