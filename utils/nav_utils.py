import os
import re
from apiclient import errors
from apiclient import http
from apiclient.http import MediaFileUpload

path_file = os.path.expanduser('~') + "/.current_dir"
dir_id_file = os.path.expanduser('~') + "/.google_path_id"
base_mimetype = "application/vnd.google-apps."

def get_cur_dir_id():
    f = open(dir_id_file)
    val = f.read()
    f.close()
    if val == '':
        return None
    return val

def update_cur_dir_id(new_id):
    f = open(dir_id_file, "w")
    f.write(new_id)
    f.close()

def pwd():
    f = open(path_file)
    val = f.read()
    f.close()
    return val

def update_pwd(new_dir):
    f = open(path_file, "w")
    f.write(new_dir)
    f.close()

def reset_home():
    update_pwd("~")
    update_cur_dir_id("")

def upload_file(service, filename, folder, filetype):
    mimetype = base_mimetype + filetype

    media_body = MediaFileUpload(filename, mimetype=mimetype, resumable=True)

    body = {
        'title': filename,
        'description': '',
        'mimeType': 'text/plain'
    }

    if folder:
        body['parents'] = [{'id': folder['id']}]

    try:
        f = service.files().insert(body=body, media_body=media_body).execute()
        return True
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        return False


def ls(service, limit=100):
    cur_id = get_cur_dir_id()
    if not cur_id:
        cur_id = "root"
    results = ""
    children = service.children().list(folderId=cur_id).execute()
    results = []
    for child in children.get('items', []):
        results.append(service.files().get(fileId=child['id']).execute())
    return results

def lsfolder(service, folder):
    folderid = ""
    if not folder:
        folderid = 'root'
    else:
        folderid = folder['id']
    #folderid = folder['id'] if folder['id'] else 'root'
    results = ""
    children = service.children().list(folderId=folderid).execute()
    results = []
    for child in children.get('items', []):
        results.append(service.files().get(fileId=child['id']).execute())
    return results


def cd(service, folder):
    results = ls (service)
    new_id = None
    for f in results:
        if f['title'] == folder and is_folder(f):
            new_id = f['id']
    if not new_id:
        return False
    update_pwd(pwd() + "/" + folder)
    update_cur_dir_id(new_id)
    return True

def is_folder(f):
    return "application/vnd.google-apps.folder" == f['mimeType']

def is_gdoc(f):
    return "application/vnd.google-apps.document" == f['mimeType']

def delete(service, f):
    try:
        service.files().delete(fileId=f['id']).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def find_recursive(service, pattern, folder, path):
    files = lsfolder(service, folder)
    matches = []
    for file in files:
        if is_folder(file):
            matches += find_recursive(service, pattern, file, path + "/" + file['title'])
        elif len(re.findall(pattern, file['title'])) != 0:
            matches.append((path+"/"+file['title'], file))
    return matches

def find(service, folder, pattern):
    getFolderPartial(service, folder)
    return find_recursive(service, pattern, getFile(service, folder.split("/")[-1]), pwd())
    reset_home()

def read(service, f):
    contents = ""
    try:
        files = service.files()
        fileId = f['id']
        if is_gdoc(f):
            download_url = files.get(fileId=fileId).execute()['exportLinks']['text/plain']
            resp, contents = service._http.request(download_url)
            if resp.status != 200:
                #print 'An error occurred: %s' % error
                return None
        else:
            contents = files.get_media(fileId=fileId).execute()
        #print 'Contents:', contents
    except errors.HttpError, error:
        #print 'An error occurred: %s' % error
        return None
    return contents

def getFile(service, fname):
    results = ls(service)
    for file in results:
        if (file['title'] == fname):
            return file
    return None

def getFolder(service, path):
    folders = path.split("/")
    if (len(folders)==0):
        return True
    if (len(folders)==1):
        if (folders[0] == '~') :
            reset_home()
        return cd(service, folders[0])
    for folder in folders:
        if (folder == '~'):
            reset_home()
        elif (not cd(service, folder)):
            return False
    return True

def getFolderPartial(service, path):
    folders = path.split("/")[:-1]
    if (len(folders)==0):
        return True
    if (len(folders)==1):
        if (folders[0] == '~') :
            reset_home()
        return cd(service, folders[0])
    for folder in folders:
        if (folder == '~'):
            reset_home()
        elif (not cd(service, folder)):
            return False
    return True



