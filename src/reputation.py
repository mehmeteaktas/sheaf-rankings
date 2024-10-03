import pandas as pd
import xml.etree.ElementTree as ET
import re


#This should be the posts.xml file
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
relevant_user_ids = set([user_id for sublist in df7_first_100["Id"] for user_id in sublist])
df_relevant = df[df["Id"].isin(relevant_user_ids)]
##############
##############

invalid_entries_count = df_relevant["OwnerUserId"].isna().sum()


df_posts = df_relevant
#df_posts = pd.read_xml('datascience.stackexchange.com/Posts.xml', xpath='.//row', parser='etree')

#This should be the respective votes.xml and posthistory.xml file from whatever stack exchange dataset you will use
df_votes = pd.read_xml('Votes.xml', xpath='.//row', parser='etree')
df_posthistory = pd.read_xml('PostHistory.xml', xpath='.//row', parser='etree')
df_votes = df_votes[df_votes["PostId"].isin(relevant_user_ids)]
df_posthistory = df_posthistory[df_posthistory["PostId"].isin(relevant_user_ids)]
print(df_votes.head(10))
print(df_posts.head(10))

#Key is userid and tag, value is how many gotten from suggested edit
edit_dict_outer = {}
edit_dict_inner = {}

def post_value(post_id, day):
    relevant_slice = df_votes[(df_votes["PostId"] == post_id) & (df_votes["CreationDate"] == day)]
    upvotes = 10*(relevant_slice["VoteTypeId"] == 2).sum()
    downvotes = -2*(relevant_slice["VoteTypeId"] == 3).sum()
    value = upvotes - downvotes 
    return value


def extract_proposed_by_id(text):
    # Define the pattern to match the proposed by user ID
    pattern = r'Proposed by (\d+)'
    
    # Use re.search to find the first occurrence of the pattern in the text
    match = re.search(pattern, text)
    
    # If a match is found, return the user ID
    if match:
        return match.group(1)
    else:
        return None
    
def suggested_edits_for_day(day):
    relevant_slice = df_posthistory[(df_posthistory["CreationDate"] == day)]
    accepted_edits = relevant_slice[relevant_slice["PostHistoryTypeId"] == 24]
    useridlist = []
    postidlist = []
    for index, row in accepted_edits.iterrows():
        useridlist.append(extract_proposed_by_id(row["Comment"]))
        postidlist.append(row["PostId"])
   # print(useridlist, postidlist)
    return useridlist, postidlist


daylist = df_votes["CreationDate"].unique().tolist()
post_list = df_posts["Id"].unique().tolist()


outer_dict = {}
inner_dict = {}


daysum = 0
for day in daylist:
    outer_dict_day = {}
    inner_dict_day = {}
    daysum = 0
    intdf = df_votes[df_votes["CreationDate"] == day]
    post_list = intdf["PostId"].unique().tolist()
    for post in post_list:
        value = post_value(post, day)
        intdict = df_posts[df_posts["Id"] == post]
        userid = intdict["OwnerUserId"].values[0]
        inner_dict_day = outer_dict_day.get(userid, {})
        tags = intdict["Tags"].values[0]
        for tag in tags:
            if tag not in inner_dict_day:
                inner_dict_day[tag] = 0
            inner_dict_day[tag] += inner_dict_day.get(tag, 0) + value
        outer_dict_day[userid] = inner_dict_day
    useridlist, postidlist = suggested_edits_for_day(day)
    for user, post in zip(useridlist, postidlist):
        intdict = df_posts[df_posts["Id"] == post]
        tags = intdict["Tags"]
        inner_dict_day = outer_dict_day.get(userid, {})
        for tag in tags:
            if tag not in inner_dict_day:
                inner_dict_day[tag] = 0
            int_edit = edit_dict_outer.get(edit_dict_inner, {})
            int_int_edit = int_edit.get(tag, 0)
            if int_int_edit > 1000:
                pass

            else:
                inner_dict_day[tag] += inner_dict_day.get(tag, 0) + 2
                int_int_edit += 2
                int_edit[tag] = int_int_edit
                edit_dict_outer[tag] = int_edit
        outer_dict_day[userid] = inner_dict_day
    
    for user in outer_dict_day:
        intdict = outer_dict.get(user, {})
        for tag in outer_dict_day[user]:
            if outer_dict_day[user][tag] > 200:
                outer_dict_day[user][tag] = 200
            intval = intdict.get(tag, 0)
            intval += outer_dict_day[user][tag]
            intdict[tag] = intval
        outer_dict[user] = intdict
    
            
#Bounty removal
intdf = df_votes[df_votes["VoteTypeId"] == 8]
for index, row in intdf.iterrows():
    user = row["UserId"]
    bountyamount = row["BountyAmount"]
    postid = row["PostId"]
    intdict = df_posts[df_posts["Id"] == postid]
    tags = intdict["Tags"].values[0]
    int_inner_dict = outer_dict.get(user, {})
    for tag in tags:
        int_tag_score = int_inner_dict.get(tag, 0)
        int_tag_score += -1*bountyamount
        int_inner_dict[tag] = int_tag_score
    outer_dict[user] = int_inner_dict

intdf = df_votes[df_votes["VoteTypeId"] == 9]
for index, row in intdf.iterrows():
    user = row["UserId"]
    bountyamount = row["BountyAmount"]
    postid = row["PostId"]
    intdict = df_posts[df_posts["Id"] == postid]
    tags = intdict["Tags"].values[0]
    int_inner_dict = outer_dict.get(user, {})
    for tag in tags:
        int_tag_score = int_inner_dict.get(tag, 0)
        int_tag_score += bountyamount
        int_inner_dict[tag] = int_tag_score
    outer_dict[user] = int_inner_dict




#Bounty Add
# Offensive Tags
# Accepted Answer
    
off_spam = [12, 4]
post_list = df_posts["Id"].unique().tolist()

for post in post_list:
    int_df = df_votes[(df_votes["PostId"] == post) & (df_votes["VoteTypeId"].isin(off_spam))]
    count = int_df["VoteTypeId"].count()
    if count >= 6:
        intdict = df_posts[df_posts["Id"] == postid]
        user = intdict["OwnerUserId"].values[0]
        tags = intdict["Tags"].values[0]
        int_inner_dict = outer_dict.get(user, {})
        for tag in tags:
            int_tag_score = int_inner_dict.get(tag, 0)
            int_tag_score += -100
            int_inner_dict[tag] = int_tag_score
        outer_dict[user] = int_inner_dict


for index, row in df_posts.iterrows():
    if pd.notna(row["AcceptedAnswerId"]):
        int_df = df_posts[df_posts["Id"] == row["AcceptedAnswerId"]]
        if int_df.empty:
            print("Empty")
            continue
        userid = int_df["OwnerUserId"].values[0]
        tags = row["Tags"]
        int_inner_dict = outer_dict.get(userid, {})
        for tag in tags:
            int_tag_score = int_inner_dict.get(tag, 0)
            int_tag_score += 15
            int_inner_dict[tag] = int_tag_score
        outer_dict[userid] = int_inner_dict

        userid = row["OwnerUserId"]
        print("acceptedUser", userid)
        int_inner_dict = outer_dict.get(userid, {})
        for tag in tags:
            int_tag_score = int_inner_dict.get(tag, 0)
            int_tag_score += 2
            int_inner_dict[tag] = int_tag_score
        outer_dict[userid] = int_inner_dict






dictt = {}
taglist = []
for index, row in df_posts.iterrows():
    taglist = []
    intlist = dictt.get(row["OwnerUserId"], [])
    taglist = row["Tags"]
    for tag in taglist:
        intlist.append(tag)
    dictt[row["OwnerUserId"]] = intlist

for user, tags in dictt.items():
    if user not in outer_dict:
        outer_dict[user] = {}
    for tag in tags:
        if tag not in outer_dict[user]:
            outer_dict[user][tag] = 0

records = []
for user_id, tags in outer_dict.items():
    for tag, score in tags.items():
        records.append({"UserId": user_id, "Tag": tag, "Score": score})

df_outer_dict = pd.DataFrame(records)
df_outer_dict = df_outer_dict.sort_values(by=['Tag', 'Score'], ascending=[True, False])
df_outer_dict = df_outer_dict.dropna(subset=['UserId'])

# Save to CSV
csv_path = 'reputation.csv'
df_outer_dict.to_csv(csv_path, index=False)


