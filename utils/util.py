from urllib import request

def get_web_content(url_str):
    try:
        response = request.urlopen(url_str)
        status = response.status
        content = response.read() if status == 200 else "Error: " + str(status)
        return status, content
    except Exception as e:
        return -1, "Error: " + str(e)



# test functions
if __name__ == '__main__':
    print(get_web_content("www.com"))
