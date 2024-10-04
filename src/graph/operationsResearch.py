#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
df = pd.read_xml('ORPosts.xml', xpath='.//row', parser= 'etree')
for index, row in df.iterrows():
    if pd.isna(row['ParentId']):
        df.at[index,'ParentId'] = row['Id']
    else:
         df.at[index, 'Tags'] = df.loc[df['Id']==row['ParentId'], 'Tags'].iloc[0]


# In[2]:


null_values = df['OwnerUserId'].isnull()
special_count = null_values.sum()
counting = df['ParentId'].nunique()
print(counting)
print(special_count)
print(df.shape[0])
df.head(20)


# In[3]:


df["Tags"] = df["Tags"].map(lambda x: x.strip('|').split('|') if x else [])

df_exploded = df.explode('Tags')

full_power = df_exploded.groupby(['OwnerUserId','Tags']).sum().reset_index()
full_power.head(20)


# In[4]:


arr = [0] * (df.shape[0]-special_count)
narr = [0] * (df.shape[0]-special_count)
big_count = 0
for index, row in df.iterrows():
    count = 0
    vector_spice = np.zeros(len(row['Tags']))
    name_spice = [0] * len(row['Tags'])
    while count < len(row['Tags']):
        if not pd.isna(df.at[index,'OwnerUserId']):
            vector_spice[count] = full_power.loc[(full_power['OwnerUserId']==row['OwnerUserId']) & (full_power['Tags']==row['Tags'][count])]['Score'].iloc[0]
            name_spice[count] = row['Tags'][count]
            count += 1
        else:
            count += 1
    if not pd.isna(df.at[index,'OwnerUserId']):
        arr[big_count] = vector_spice
        narr[big_count] = name_spice
        big_count += 1


# In[5]:


vector_dict = {}
namey_dict = {}
counter = 0
namey_counter = 0
for index, row in df.iterrows():
    if not pd.isna(df.at[index,'OwnerUserId']):
        vector_dict[row['Id']] = arr[counter]
        namey_dict[row['Id']] = narr[counter]
        counter += 1
    else:
        namey_counter += 1
#added a column of vectors


# In[7]:


indexing_dict = {}
count = 0
for index,row in df.iterrows():
    if not pd.isna(df.at[index,'OwnerUserId']):
        if row['OwnerUserId'] not in indexing_dict:
            indexing_dict[row['OwnerUserId']] = count
            count += 1
#created an indexing dictionary
#now we must assign the individual rows and connections (a way to find connections)
    


# In[8]:


post_grouping = [0] * df['ParentId'].nunique() 
big_count = 0
poster_grouping = [0] * df['ParentId'].nunique()

for index,row in df.iterrows():
    if row['ParentId'] not in poster_grouping:
        if not pd.isna(df.at[index,'OwnerUserId']):
            poster_grouping[big_count] = row['ParentId']
            post_grouping[big_count] = list()
            post_grouping[big_count].append((row['OwnerUserId'],row['Id']))
            big_count += 1
        else:
            ("")
    elif row['ParentId'] in poster_grouping:
        if not pd.isna(df.at[index,'OwnerUserId']):
            post_grouping[poster_grouping.index(row['ParentId'])].append((row['OwnerUserId'],row['Id']))
        else:
            ("")
print(post_grouping)


# In[9]:


def count_edges(post_grouping):
    num_edges = 0
    for key in post_grouping:
        check = True
        if isinstance(key, list):
            for i in namey_dict[key[0][1]]:
                print(i)
                if i == 'optimization':
                    check = False
            if check == False:
                num_edges += ((len(key)-1)*len(key))/2
            
    return num_edges

num_edges = count_edges(post_grouping)

def count_vertices(post_grouping):
    internal_dict = {}
    num_vertices = 0
    arr = []
    for post in post_grouping:
        if isinstance(post,list):
            for tup in post:
                if (isinstance(tup, tuple)):
                    if 'optimization' not in namey_dict[tup[1]]:
                        break;
                    if tup[0] not in arr:
                        internal_dict[tup[0]] = []
                        for i in namey_dict[tup[1]]:
                            internal_dict[tup[0]].append(i)
                        arr.append(tup[0])
                        print(len(vector_dict[tup[1]]))
                        num_vertices += len(vector_dict[tup[1]])
                    else:
                        for i in namey_dict[tup[1]]:
                            if i not in internal_dict[tup[0]]:
                                internal_dict[tup[0]].append(i)
                                num_vertices += 1
    return num_vertices, internal_dict

num_vertices, internal_dict = count_vertices(post_grouping)

print(num_edges, num_vertices)

coboundary = np.zeros((int(num_edges),num_vertices))


# In[10]:


coboundary
def get_new_indices(post_grouping, internal_dict):
    indices_map = {}
    count = 0
    for post in post_grouping:
        if isinstance(post, list):
            if 'optimization' not in namey_dict[post[0][1]]:
                continue;
            for tup in post:
                if tup[0] not in indices_map:
                    indices_map[tup[0]] = count
                    print(len(internal_dict[tup[0]]))
                    count += len(internal_dict[tup[0]])
    return indices_map

indices_map = get_new_indices(post_grouping, internal_dict)
print(internal_dict)


# In[11]:


indices_map


# In[12]:


#Algorithm
#needs fixing
def get_names_arr(post_grouping, internal_dict, num_vertices, indices_map):
    count = 0
    names_arr = [0] * num_vertices
    for post in post_grouping:
        if isinstance(post, list):
            if 'optimization' not in namey_dict[post[0][1]]:
                continue;
            for tup in post:
                for i in namey_dict[tup[1]]:
                    names_arr[indices_map[tup[0]] + internal_dict[tup[0]].index(i)] = i
    return names_arr
        
    
    
def draw_edges(coboundary, post_grouping, indices_map, internal_dict):
    i_counter = 0
    counter = 0
    tracker = 0
    for post in post_grouping:
        if isinstance(post, list):
            if 'optimization' not in namey_dict[post[0][1]]:
                continue;
            tracker = 0
            for tup in post:
                tracker = post.index(tup)+1
                while tracker<len(post):
                    if (post.index(tup) != len(post)-1): #kind of unnecessary line but keep it
                        for i in vector_dict[post[tracker][1]]:
                            coboundary[counter,indices_map[post[tracker][0]]+internal_dict[post[tracker][0]].index(namey_dict[post[tracker][1]][i_counter])] = i
                            i_counter += 1
                        i_counter = 0
                        for i in vector_dict[tup[1]]:
                            coboundary[counter,indices_map[tup[0]]+internal_dict[tup[0]].index(namey_dict[tup[1]][i_counter])] = -i
                            i_counter += 1
                        i_counter = 0
                    tracker += 1
                    counter += 1
    print(coboundary)
    return coboundary
   


# In[13]:


coboundary = draw_edges(coboundary,post_grouping,indices_map, internal_dict)
names_arr = get_names_arr(post_grouping, internal_dict, num_vertices, indices_map)


# In[14]:


print(names_arr)


# In[15]:


print(coboundary)


# In[16]:


def get_laplacian(coboundary):
    transpose = coboundary.T
    laplacian = np.matmul(transpose,coboundary)
    return laplacian

laplacian = get_laplacian(coboundary)


# In[17]:


laplacian


# In[18]:


eigenvalues, eigenvectors = np.linalg.eig(laplacian)


# In[19]:


eigenvalues


# In[20]:


eigenvalues = eigenvalues.real
len(names_arr)


# In[21]:


eigenvalues
sum_laplace = 0
for i in range(len(eigenvalues)):
    sum_laplace += (eigenvalues[i]**2)
sum_laplace


# In[22]:


centrality = []
for i in range(len(names_arr)):
    if names_arr[i] == 'optimization':
        modified_matrix = np.delete(coboundary, i, axis=1)
        laplacian = get_laplacian(modified_matrix)
        eigenvalues, eigenvectors = np.linalg.eig(laplacian)
        eigenvalues = eigenvalues.real
        summer_laplace = 0
        for i in range(len(eigenvalues)):
            summer_laplace += (eigenvalues[i]**2)
        centrality.append(summer_laplace)
centrality


# In[23]:


def calculate_centralities(sum_laplace, centrality):
    centralities = []
    for i in centrality:
        score = (sum_laplace-i)/(sum_laplace)
        centralities.append(score)
    return centralities

centralities = calculate_centralities(sum_laplace, centrality)


# In[24]:


centralities


# In[25]:


def find_max(matrix):
    max = 0
    for i in range(len(matrix)):
        if (matrix[i] > max):
            max = matrix[i]
    return max


# In[26]:


find_max(centralities)


# In[27]:


#we are here
def get_owners(post_grouping, num_vertices, internal_dict, indices_map):
    arr = [0] * num_vertices
    for post in post_grouping:
        if isinstance(post, list):
            if 'optimization' not in namey_dict[post[0][1]]:
                continue;
            for tup in post:
                for i in namey_dict[tup[1]]:
                    arr[indices_map[tup[0]] + internal_dict[tup[0]].index(i)] = tup[0]
    return arr
owners = get_owners(post_grouping, num_vertices, internal_dict, indices_map)


# In[28]:


owners


# In[29]:


len(owners)


# In[30]:


def tupify(owners, names_arr, centralities):
    arr = [0] * len(centralities)
    count = 0
    for i in range(len(names_arr)):
        if (names_arr[i] == 'optimization'):
            if (count < len(arr) and i < len(owners) and i < len(names_arr) and count < len(centralities)):
                arr[count] = (owners[i],names_arr[i],centralities[count])
            count += 1
    return arr


# In[31]:


scorings = tupify(owners, names_arr, centralities)
scorings


# In[32]:


max = 0
for i in scorings:
    if i[2] > max:
        tup = i
        max = i[2]
print(tup)


        


# In[33]:


uniqim = []
for i in owners:
    if i not in uniqim:
        uniqim.append(i)
len(uniqim)


# In[34]:


import csv

with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(scorings)


# In[35]:


final_df = pd.read_csv('output.csv',header=None)
final_df.columns = ['Owner','Tag','Centrality']


# In[36]:


final_df


# In[37]:


final_df['Rank'] = final_df['Centrality'].rank(method='dense', ascending=False)
final_df = final_df.sort_values(by='Rank')
final_df = final_df.reset_index(drop=True)
final_df.head(20)


# In[38]:


final_df.to_csv('or.csv', index=False)


# In[ ]:




