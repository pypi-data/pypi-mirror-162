import os
import time
input_dir = 'D:/'
output_dir = 'S:/'
t1 = time.time()



def search_directory(input_dir, output_dir, search_dir, ac_list, depth):
    # print(directory)
    contents = os.listdir(search_dir)
    # print(contents)
    if 'metadata.txt' in contents:
        ac_list.append({
            'path': search_dir, 
            'output_path': os.path.join(output_dir, os.path.relpath(search_dir, input_dir))
        })
        return ac_list
    if depth == 0: return ac_list
    for item in contents:
        item_path = os.path.join(search_dir, item)
        print('isdir {}: {}'.format(item_path, os.path.isdir(item_path)))
        if os.path.isdir(item_path) and 'DST' not in item:
            try:
                ac_list = search_directory(input_dir, output_dir, item_path, ac_list, depth-1)
            except: pass
    return ac_list
     
directories = search_directory(input_dir, output_dir, input_dir, list(), depth=3)

print('directories:')
print(directories)
