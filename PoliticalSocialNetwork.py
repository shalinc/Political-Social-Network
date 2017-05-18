# coding: utf-8

"""
Collecting a political social network

The goal is to use the Twitter API to construct a social network of four presidential 
candidates accounts. We used the networkx library to plot these links, 
as well as printed some statistics of the resulting graph.
"""

# Imports you'll need.
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI


consumer_key = #consumer_key here
consumer_secret = #secret key here
access_token = #access token here
access_token_secret = #access secret here


def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def read_screen_names(filename):
    """
    Read a text file containing Twitter screen_names, one per line.

    Params:
        filename....Name of the file to read.
    Returns:
        A list of strings, one per screen_name, in the order they are listed
        in the file.

    """
    ###TODO-- Completed

    #open the filename to be read
    with open(filename) as in_file:
        screen_names = in_file.readlines()

    #stripping off the additional '\n' variables generated while reading from file
    screen_names = [name.strip() for name in screen_names]
    #print(screen_names)

    return screen_names


# The method below is to handle Twitter's rate limiting.
# You should call this method whenever you need to access the Twitter API.
def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


def get_users(twitter, screen_names):
    """Retrieve the Twitter user objects for each screen_name.
    Params:
        twitter........The TwitterAPI object.
        screen_names...A list of strings, one per screen_name
    Returns:
        A list of dicts, one per user, containing all the user information
        (e.g., screen_name, id, location, etc)

    """
    ###TODO-- Completed

    #create a request for Twitter to fetch data, using robust_request function, limiting to 200
    #get the requests for every screen_name and store it in a list
    requests = [robust_request(twitter,'users/lookup',{'screen_name':screen_name, 'count':200}).json()[0] for screen_name in screen_names]

    #for request in requests:
    #    print(request)

    return requests


def get_friends(twitter, screen_name):
    """ Return a list of Twitter IDs for users that this person follows, up to 5000.

    Args:
        twitter.......The TwitterAPI object
        screen_name... a string of a Twitter screen name
    Returns:
        A list of ints, one per friend ID, sorted in ascending order.
    """
    ###TODO-- Completed

    #Requesting twitter with query to get friends of all the screen_name(s) passed as a parameter
    friends_ids = robust_request(twitter,'friends/ids',{'screen_name':screen_name}).json()

    #Returns a dictionary having several values, selecting the one which has KEY: ids,
    # i.e. get ids of all the friends in a sorted manner
    return sorted(friends_ids['ids'])



def add_all_friends(twitter, users):
    """ Get the list of accounts each user follows.
    I.e., call the get_friends method for all 4 candidates.

    Store the result in each user's dict using a new key called 'friends'.

    Args:
        twitter...The TwitterAPI object.
        users.....The list of user dicts.
    Returns:
        Nothing
    """
    ###TODO-- Completed

    #calling get_friends here to receive friends ID's for all the values of screen_name,
    # limiting the values to receive to 5000
    for user in users:
        user['friends'] = get_friends(twitter, user['screen_name'])[:5000]
        #print(len(user['friends']))



def print_num_friends(users):
    """Print the number of friends per candidate, sorted by candidate name.
    See Log.txt for an example.
    Args:
        users....The list of user dicts.
    Returns:
        Nothing
    """
    ###TODO-- Completed

    #Creating a new dictionary to store the KEY, VALUE pair for friends of every screen_name i.e. user
    # and their counts i.e. number of friends per user
    all_friends_dict = {}

    for user in users:
        all_friends_dict[user['screen_name']] = len(user['friends'])

    for candidate in sorted(all_friends_dict):
        print(candidate,all_friends_dict[candidate])


def count_friends(users):
    """ Count how often each friend is followed.
    Args:
        users: a list of user dicts
    Returns:
        a Counter object mapping each friend to the number of candidates who follow them.
   
    """
    ###TODO-- Completed

    #Creating a Counter object, to count the mapping
    c = Counter()
    c.update(friend_id for user in users for friend_id in user['friends'])
    return c



def friend_overlap(users):
    """
    Compute the number of shared accounts followed by each pair of users.

    Args:
        users...The list of user dicts.

    Return: A list of tuples containing (user1, user2, N), where N is the
        number of accounts that both user1 and user2 follow.  
	"""
    ###TODO-- Completed

    #Creating a list of tuples to store the values for number of shared accounts by each of the user
    overlap_tuples = []

    #Trying for all the combination if user's without repetition
    for outer_idx,_ in enumerate(users):
        for inner_idx,_ in enumerate(users):
            if (inner_idx != len(users)-1) and (outer_idx < inner_idx+1):
                #Creating a SET of friends for 2 users and finding the INTERSECTION i.e. Common friends between these users
                overlap_tuples.append(tuple((users[outer_idx]['screen_name'],users[inner_idx+1]['screen_name'],
                                             len(list(set(users[outer_idx]['friends']) & set(users[inner_idx+1]['friends']))))))

    #Sort based on first KEY as N i.e. number of shared account in descending order,
    # for ties break using screen_name of user one, further on screen_name of user two
    return sorted(overlap_tuples, key=lambda x:[-x[2], x[0], x[1]])

    #for perm in combinations(screen_names,2):
    #    overlap_tuples.append(tuple(perm[0],perm[1],len(list(set(user[perm[0]]['friends']) & set(perm[1]['friends'])))))
        #print(len(list(set(users[0]['friends']) & set(users[1]['friends']))))


def followed_by_hillary_and_donald(users, twitter):
    """
    Find and return the screen_name of the one Twitter user followed by both Hillary
    Clinton and Donald Trump. Using the TwitterAPI to convert
    the Twitter ID to a screen_name. 
    Params:
        users.....The list of user dicts
        twitter...The Twitter API object
    Returns:
        A string containing the single Twitter screen_name of the user
        that is followed by both Hillary Clinton and Donald Trump.
    """
    ###TODO-- Completed
    for user in users:
        if user['screen_name'] == 'HillaryClinton':
            friends_Hillary = user['friends']
            #print(len(friends_Hillary))
        elif user['screen_name'] == 'realDonaldTrump':
            friends_donald = user['friends']
            #print(len(friends_donald))

    common_followed_id = list(set(friends_Hillary) & set(friends_donald))

    commn_followed_user = robust_request(twitter,'users/lookup',{'user_id':common_followed_id}).json()
    #print(commn_followed_user[0]['screen_name'])#['screen_name'])
    return commn_followed_user[0]['screen_name']
    #pass


def create_graph(users, friend_counts):
    """ Create a networkx undirected Graph, adding each candidate and friend
        as a node.  Note: while all candidates should be added to the graph,
        only add friends to the graph if they are followed by more than one
        candidate. (This is to reduce clutter.)

        Each candidate in the Graph will be represented by their screen_name,
        while each friend will be represented by their user id.

    Args:
      users...........The list of user dicts.
      friend_counts...The Counter dict mapping each friend to the number of candidates that follow them.
    Returns:
      A networkx Graph
    """
    ###TODO-- Completed
    G = nx.Graph()

    #For Filtering the Nodes
    #print(friend_counts)
    friend_nodes = [friend for friend in friend_counts if friend_counts[friend] > 1]
    candidate_nodes = [user['screen_name'] for user in users]

    #print("Nodes: ",len(friend_nodes), len(candidate_nodes))
    #Adding Nodes to graph
    G.add_nodes_from(friend_nodes + candidate_nodes)

    #Connecting the Nodes with Edges
    for candidate in users:
        for friend in friend_nodes:
            if friend in candidate['friends']:
                G.add_edge(candidate['screen_name'], friend)

    return G


def draw_network(graph, users, filename):
    """
    Draw the network to a file. Only label the candidate nodes; the friend
    nodes should have no labels (to reduce clutter).
    """
    ###TODO-- Completed
    candidate_names = [user['screen_name'] for user in users]
    plt.figure(figsize=(12,12))
    candidate_labels = {node: node if node in candidate_names else '' for node in graph.nodes_iter()}
    #print(candidate_labels)
    nx.draw_networkx(graph, labels=candidate_labels, alpha=0.5, node_color='r', node_size=100, width=0.1)
    #plt.show()
    plt.axis('off')
    plt.savefig(filename)
    #pass


def main():
    """ Main method. You should not modify this. """
    twitter = get_twitter()
    screen_names = read_screen_names('candidates.txt')
    print('Established Twitter connection.')
    print('Read screen names: %s' % screen_names)
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    print('User followed by Hillary and Donald: %s' % followed_by_hillary_and_donald(users, twitter))

    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')


if __name__ == '__main__':
    main()
