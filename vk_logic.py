import vk
import re
from tokens import VK_TOKEN

vk_api = vk.API(access_token=VK_TOKEN, v= '5.131')

'''Converting user's link to a list of values for VK API'''
def link_transform(link):
    res_id = ['','',''] 
    pattern_comment = r"_r+\d+|reply=\d+"
    pattern_post = r"-?\d+_\d+"
    res_post = re.findall(pattern_post, link)
    res_comment = re.findall(pattern_comment, link)
    if len(res_comment) == 0:
        result_id = res_post[0].split('_')
        res_id[0] = result_id[0]
        res_id[1] = result_id[1]
    else:
        result_id = res_post[0].split('_')
        if res_comment[0].startswith('_r'):
            result_id_rep = res_comment[0].split('_r')
        else:
            result_id_rep = res_comment[0].split('reply=')
        res_id[0] = result_id[0]
        res_id[1] = result_id[1]
        res_id[2] = result_id_rep[1]
    return res_id

'''Resolving screen name to id (for ban only)'''
def screen_name_to_id(link):
    user_id = ['']
    pattern_id = r"id\d+"
    pattern_name = r"\w+(?![https://vk.com/])"
    res_id = re.findall(pattern_id, link)
    res_name = re.findall(pattern_name, link)
    if len(res_id) == 0:
        to_id = vk_api.utils.resolveScreenName(screen_name = res_name[0])
        id = [*to_id.values()]
        user_id[0] = id[0]
    else:
        result_id = res_id[0].split('id')
        user_id[0] = result_id[1]
    return user_id
    
'''VK API methods'''
def vk_open(data):
    if vk_api.wall.openComments(owner_id = data[0], post_id = data[1]):
        return True
    else:
        False

def vk_close(data):
    if vk_api.wall.closeComments(owner_id = data[0], post_id = data[1]):
        return True
    else:
        False

def vk_delete(data):
    if vk_api.wall.deleteComment(owner_id = data[0], comment_id = data[2]):
        return True
    else:
        False

def vk_restore(data):
    if vk_api.wall.restoreComment(owner_id = data[0], comment_id = data[2]):
        return True
    else:
        False

def vk_restore_post(data):
    if vk_api.wall.restore(owner_id = data[0], post_id = data[1]):
        return True
    else:
        False

def vk_ban(data):
    if vk_api.account.ban(owner_id = data[0]):
        return True
    else:
        False

def get_comment(data):
    id = vk_api.wall.getComment(owner_id = data[0], comment_id = data[2], extended = 1)
    res_id = [i['id'] for i in id['profiles']]
    return res_id

def vk_unban(data):
    if vk_api.account.unban(owner_id = data[0]):
        return True
    else:
        False

