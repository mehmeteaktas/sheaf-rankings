#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
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

print(df_cleaned['Tags'].nunique())

df_exploded.head(20)


# In[2]:


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


# In[3]:


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


# In[4]:


import networkx as nx


# In[5]:


def adding_edges(post_grouping, poster_grouping, tag_itself, by_tag):
    graphs = dict()
    question = None
    for tag in tag_itself:
        if tag == "human-biology":
            graphs[tag] = nx.DiGraph()
            for i in range(len(post_grouping)):
                if isinstance(post_grouping[i], list):
                    if (poster_grouping[i] in by_tag[tag_itself.index(tag)]):
                        for tup in post_grouping[i]:
                            if tup[1] == True and not graphs[tag].has_node(tup[0]):
                                graphs[tag].add_node(tup[0])
                                question = tup[0]
                        for tup in post_grouping[i]:
                            if tup[1] == False and not graphs[tag].has_node(tup[0]):
                                graphs[tag].add_node(tup[0])
                                graphs[tag].add_edge(question,tup[0])
                            elif tup[1] == False and graphs[tag].has_node(tup[0]):
                                graphs[tag].add_edge(question,tup[0])   
                    else:
                        ("")
    return graphs
        
        
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)
print(len(by_tag[tag_itself.index('human-biology')]))


# In[6]:


import matplotlib.pyplot as plt
pos = nx.spring_layout(graphs['human-biology'])
nx.draw(graphs['human-biology'], pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=15)


# In[7]:


pageranks = []
for key in graphs:
    pr = nx.pagerank(graphs[key])
    pageranks.append(pr)
pageranks


# In[8]:


final_ranking = []
for i in range(len(pageranks)):
    sorted_pairs = sorted(pageranks[i].items(), key=lambda x: x[1], reverse=True)
    final_ranking.append(sorted_pairs)
final_ranking


# In[9]:


arr = []
users = [x[0] for x in final_ranking[0]]
arr.append({"human-biology": users})
arr


# In[10]:


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
        
        


# In[11]:


df = pd.DataFrame(flattened_data, columns=['Tag', 'OwnerUserId', 'Rank'])

# Save to CSV
df.to_csv('BiologyPageRankoutput.csv', index=False)

print("CSV file created successfully.")


# In[ ]:




