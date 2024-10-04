#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
df = pd.read_xml('LatinPosts.xml', xpath='.//row', parser= 'etree')

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
        if tag == "english-to-latin-translation":
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
pos = nx.spring_layout(graphs['english-to-latin-translation'])
nx.draw(graphs['english-to-latin-translation'], pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=15)


# In[ ]:

#doing Sheaf Laplacian
ordered_df = pd.read_csv('latin.csv')
sheaf_laplacian = [0]*len(ordered_df)
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['english-to-latin-translation']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    sheaf_laplacian[count] = sum
    count = count + 1
    if (graphs['english-to-latin-translation'].has_node(row['Owner'])):
        graphs['english-to-latin-translation'].remove_node(row['Owner'])

temp = sheaf_laplacian[0]
for i in range(len(sheaf_laplacian)):
    sheaf_laplacian[i] = (sheaf_laplacian[i]/temp)


# In[ ]:
#doing NonSheaf Laplacian
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('NonSheafLaplacianLatin.csv') #change
laplacian = [0]*len(ordered_df)
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['english-to-latin-translation']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    laplacian[count] = sum
    count = count + 1
    if (graphs['english-to-latin-translation'].has_node(row['Owner'])):
        graphs['english-to-latin-translation'].remove_node(row['Owner'])

temp = laplacian[0]
for i in range(len(laplacian)):
    laplacian[i] = (laplacian[i]/temp)


# In[ ]:
#doing SIR
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('LatinSIROutput.csv') #change
sir = [0]*len(ordered_df)
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['english-to-latin-translation']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    sir[count] = sum
    count = count + 1
    if (graphs['english-to-latin-translation'].has_node(row['OwnerUserId'])):
        graphs['english-to-latin-translation'].remove_node(row['OwnerUserId'])
temp = sir[0]
for i in range(len(sir)):
    sir[i] = (sir[i]/temp)

#doing page rank
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('LatinPageRankoutput.csv') #change
page_rank = [0]*len(ordered_df)
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['english-to-latin-translation']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    page_rank[count] = sum
    count = count + 1
    if (graphs['english-to-latin-translation'].has_node(row['OwnerUserId'])):
        graphs['english-to-latin-translation'].remove_node(row['OwnerUserId'])
temp = page_rank[0]
for i in range(len(page_rank)):
    page_rank[i] = (page_rank[i]/temp)


#doing reputation
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

ordered_df = pd.read_csv('reputation_latin.csv') #change
reputation = [0]*len(ordered_df)
count = 0

for index, row in ordered_df.iterrows():
    components = list(nx.connected_components(graphs['english-to-latin-translation']))
    sum = 0
    for i in components:
        sum += (len(i)**2)
    
    reputation[count] = sum
    count = count + 1
    if (graphs['english-to-latin-translation'].has_node(row['UserId'])):
        graphs['english-to-latin-translation'].remove_node(row['UserId'])
temp = reputation[0]
for i in range(len(reputation)):
    reputation[i] = (reputation[i]/temp)
graphs = adding_edges(post_grouping, poster_grouping, tag_itself, by_tag)

# In[ ]:


import matplotlib.pyplot as plt
plt.figure(figsize=(8,6))

x_normalized1 = [x/len(sheaf_laplacian) for x in range(len(sheaf_laplacian))]
x_normalized2 = [x/len(laplacian) for x in range(len(laplacian))]
x_normalized3 = [x/len(sir) for x in range(len(sir))]
x_normalized4 = [x/len(page_rank) for x in range(len(page_rank))]
x_normalized5 = [x/len(reputation) for x in range(len(reputation))]
plt.yscale('log')
plt.plot(x_normalized1, sheaf_laplacian, color='b', label='Graph Sheaf Laplacian')
plt.plot(x_normalized2, laplacian, color='r', label='Graph Non-Sheaf Laplacian')
plt.plot(x_normalized3, sir, color='g', label='Graph SIR')
plt.plot(x_normalized4, page_rank, color='m', label='Page Rank')
plt.plot(x_normalized5, reputation, color='c', label='Reputation')

plt.legend()

plt.title('latin')
plt.xlabel('Nodes Removed')
plt.ylabel('Connections')
plt.savefig('LatinSizeOfGiantComps.png')

